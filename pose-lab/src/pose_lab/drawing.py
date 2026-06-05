from __future__ import annotations

import cv2
import numpy as np

from .core_joints import skeleton_edges
from .types import BBox, FrameResult


def draw_overlay(
    frame: np.ndarray,
    result: FrameResult,
    model_name: str,
    layout: str,
    keypoint_threshold: float,
    valid_ratio: float,
) -> np.ndarray:
    canvas = frame.copy()
    abnormal = result.invalid_core or result.large_jump
    color = (0, 0, 255) if abnormal else (40, 210, 80)
    if result.expanded_bbox is not None:
        _draw_box(canvas, result.expanded_bbox, color, 2)
    if result.pose is not None and result.pose.has_pose:
        _draw_pose(canvas, result.pose.keypoints, result.pose.scores, layout, keypoint_threshold, color)
    _draw_hud(canvas, model_name, valid_ratio, result.core_confidence, abnormal, result.frame_index)
    return canvas


def _draw_box(frame: np.ndarray, box: BBox, color: tuple[int, int, int], thickness: int) -> None:
    p1 = (int(round(box.x1)), int(round(box.y1)))
    p2 = (int(round(box.x2)), int(round(box.y2)))
    cv2.rectangle(frame, p1, p2, color, thickness)


def _draw_pose(frame: np.ndarray, keypoints: np.ndarray, scores: np.ndarray, layout: str, threshold: float, color: tuple[int, int, int]) -> None:
    for a, b in skeleton_edges(layout):
        if a < len(scores) and b < len(scores) and scores[a] >= threshold and scores[b] >= threshold:
            pa = tuple(np.round(keypoints[a]).astype(int))
            pb = tuple(np.round(keypoints[b]).astype(int))
            cv2.line(frame, pa, pb, color, 2, cv2.LINE_AA)
    for idx, point in enumerate(keypoints):
        if idx < len(scores) and scores[idx] >= threshold:
            cv2.circle(frame, tuple(np.round(point).astype(int)), 4, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, tuple(np.round(point).astype(int)), 5, color, 1, cv2.LINE_AA)


def _draw_hud(frame: np.ndarray, model_name: str, valid_ratio: float, core_confidence: float, abnormal: bool, frame_index: int) -> None:
    lines = [
        f"Model: {model_name}",
        f"Valid ratio: {valid_ratio:.3f}",
        f"Core confidence: {core_confidence:.3f}",
        f"Frame: {frame_index}",
    ]
    if abnormal:
        lines.append("ABNORMAL")
    x, y = 18, 30
    for i, text in enumerate(lines):
        yy = y + i * 28
        cv2.putText(frame, text, (x + 1, yy + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, text, (x, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255) if not abnormal else (0, 0, 255), 2, cv2.LINE_AA)

