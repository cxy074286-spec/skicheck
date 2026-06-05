from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import numpy as np

from .core_joints import core_indices
from .types import FrameResult, PoseResult


@dataclass
class MetricAccumulator:
    model: str
    video_name: str
    total_frames: int
    layout: str
    keypoint_threshold: float
    min_core_confidence: float
    min_core_joint_count: int
    max_jump_ratio: float
    sampled_frames: int = 0
    valid_pose_frames: int = 0
    invalid_core_joint_frames: int = 0
    large_joint_jump_frames: int = 0
    core_confidences: list[float] = field(default_factory=list)
    anomalies: list[dict] = field(default_factory=list)
    started_at: float = field(default_factory=time.perf_counter)
    previous_core_points: np.ndarray | None = None

    def evaluate(self, frame_index: int, sampled_index: int, pose: PoseResult | None, frame_shape: tuple[int, int, int], bbox, expanded_bbox) -> FrameResult:
        self.sampled_frames += 1
        core = core_indices(self.layout)
        core_confidence = 0.0
        invalid_core = True
        large_jump = False
        valid = False

        if pose is not None and pose.has_pose:
            usable = [idx for idx in core if idx < len(pose.scores)]
            trusted = [idx for idx in usable if float(pose.scores[idx]) >= self.keypoint_threshold]
            if usable:
                core_confidence = float(np.mean([pose.scores[idx] for idx in usable]))
                self.core_confidences.append(core_confidence)
            invalid_core = len(trusted) < self.min_core_joint_count or core_confidence < self.min_core_confidence
            large_jump = self._has_large_jump(pose, trusted, frame_shape)
            valid = not invalid_core and not large_jump

        if valid:
            self.valid_pose_frames += 1
        if invalid_core:
            self.invalid_core_joint_frames += 1
        if large_jump:
            self.large_joint_jump_frames += 1

        if invalid_core or large_jump:
            self.anomalies.append(
                {
                    "frame_index": frame_index,
                    "sampled_index": sampled_index,
                    "invalid_core_joint": invalid_core,
                    "large_joint_jump": large_jump,
                    "core_confidence": round(core_confidence, 4),
                }
            )

        return FrameResult(
            frame_index=frame_index,
            sampled_index=sampled_index,
            bbox=bbox,
            expanded_bbox=expanded_bbox,
            pose=pose,
            core_confidence=core_confidence,
            valid=valid,
            invalid_core=invalid_core,
            large_jump=large_jump,
        )

    def _has_large_jump(self, pose: PoseResult, trusted: list[int], frame_shape: tuple[int, int, int]) -> bool:
        if not trusted:
            return False
        current = np.asarray([pose.keypoints[idx] for idx in trusted], dtype=np.float32)
        if self.previous_core_points is None or self.previous_core_points.shape != current.shape:
            self.previous_core_points = current
            return False
        diagonal = math.hypot(frame_shape[1], frame_shape[0])
        movement = np.linalg.norm(current - self.previous_core_points, axis=1)
        self.previous_core_points = current
        return bool(np.median(movement) / max(diagonal, 1.0) > self.max_jump_ratio)

    def to_json(self) -> dict:
        elapsed = time.perf_counter() - self.started_at
        ratio = self.valid_pose_frames / self.sampled_frames if self.sampled_frames else 0.0
        avg_conf = float(np.mean(self.core_confidences)) if self.core_confidences else 0.0
        return {
            "model": self.model,
            "video_name": self.video_name,
            "total_frames": self.total_frames,
            "sampled_frames": self.sampled_frames,
            "valid_pose_frames": self.valid_pose_frames,
            "valid_pose_ratio": round(ratio, 6),
            "invalid_core_joint_frames": self.invalid_core_joint_frames,
            "large_joint_jump_frames": self.large_joint_jump_frames,
            "processing_seconds": round(elapsed, 3),
            "average_core_joint_confidence": round(avg_conf, 6),
        }

