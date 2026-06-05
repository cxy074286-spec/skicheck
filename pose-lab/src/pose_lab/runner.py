from __future__ import annotations

import json
from pathlib import Path

import cv2
from tqdm import tqdm

from .bbox import crop_and_resize, expand_bbox, map_keypoints_to_frame
from .config import load_yaml
from .detectors import build_detector, select_main_person
from .drawing import draw_overlay
from .metrics import MetricAccumulator
from .models import build_pose_model
from .types import PoseResult, VideoSpec
from .video_io import iter_sampled_frames, make_writer, video_info


def run_experiment(config_path: Path, videos: list[VideoSpec], out_dir: Path, selected_models: list[str] | None = None) -> None:
    config = load_yaml(config_path)
    model_configs: dict = config.get("models", {})
    if selected_models:
        missing = sorted(set(selected_models) - set(model_configs))
        if missing:
            raise KeyError(f"Unknown model ids: {', '.join(missing)}")
        model_items = [(name, model_configs[name]) for name in selected_models]
    else:
        model_items = list(model_configs.items())
    detector = build_detector(config.get("detector", {}))
    for model_id, model_config in model_items:
        pose_model = build_pose_model(model_config)
        try:
            for video in videos:
                run_model_on_video(config, detector, pose_model, model_id, model_config, video, out_dir)
        finally:
            pose_model.close()


def run_model_on_video(config: dict, detector, pose_model, model_id: str, model_config: dict, video: VideoSpec, out_root: Path) -> None:
    video_path = video.path
    total_frames, source_fps, size = video_info(video_path)
    out_dir = out_root / model_id / video_path.stem
    sample_dir = out_dir / "sample_frames"
    sample_dir.mkdir(parents=True, exist_ok=True)
    writer = make_writer(out_dir / "debug_pose_overlay.mp4", source_fps / max(1, int(config["sampling"].get("frame_step", 5))), size)

    validity = config.get("validity", {})
    detector_config = config.get("detector", {})
    frame_step = int(config.get("sampling", {}).get("frame_step", 5))
    sample_limit = int(config.get("sampling", {}).get("sample_frame_limit", 18))
    layout = str(model_config.get("core_layout"))
    keypoint_threshold = float(validity.get("keypoint_confidence", 0.3))
    accumulator = MetricAccumulator(
        model=str(model_config.get("display_name", model_id)),
        video_name=video_path.name,
        total_frames=total_frames,
        layout=layout,
        keypoint_threshold=keypoint_threshold,
        min_core_confidence=float(validity.get("min_core_confidence", 0.35)),
        min_core_joint_count=int(validity.get("min_core_joint_count", 6)),
        max_jump_ratio=float(validity.get("max_core_joint_jump_ratio", 0.18)),
    )

    progress = tqdm(iter_sampled_frames(video_path, frame_step), desc=f"{model_id}/{video_path.name}", unit="frame")
    saved_samples = 0
    try:
        for frame_index, sampled_index, frame in progress:
            bbox = select_main_person(detector.detect(frame), frame.shape)
            expanded = None
            pose = None
            if bbox is not None:
                expanded = expand_bbox(
                    bbox,
                    frame.shape,
                    scale=float(detector_config.get("expand_scale", 1.4)),
                    bottom_bias=float(detector_config.get("bottom_bias", 0.65)),
                )
                try:
                    crop, sx, sy = crop_and_resize(frame, expanded, int(model_config.get("input_short_edge", detector_config.get("crop_short_edge", 640))))
                    crop_pose = pose_model.predict(crop)
                    if crop_pose is not None and crop_pose.has_pose:
                        mapped = map_keypoints_to_frame(crop_pose.keypoints, expanded, sx, sy)
                        pose = PoseResult(mapped, crop_pose.scores, crop_pose.raw)
                except ValueError:
                    pose = None

            frame_result = accumulator.evaluate(frame_index, sampled_index, pose, frame.shape, bbox, expanded)
            valid_ratio = accumulator.valid_pose_frames / accumulator.sampled_frames if accumulator.sampled_frames else 0.0
            overlay = draw_overlay(frame, frame_result, accumulator.model, layout, keypoint_threshold, valid_ratio)
            writer.write(overlay)
            if saved_samples < sample_limit and (sampled_index % max(1, sample_limit // 3) == 0 or frame_result.invalid_core or frame_result.large_jump):
                status = "bad" if frame_result.invalid_core or frame_result.large_jump else "ok"
                cv2.imwrite(str(sample_dir / f"{sampled_index:05d}_{status}_frame{frame_index}.jpg"), overlay)
                saved_samples += 1
    finally:
        writer.release()

    _write_json(out_dir / "metrics.json", accumulator.to_json())
    _write_json(out_dir / "anomaly_frames.json", {"anomalies": accumulator.anomalies})


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

