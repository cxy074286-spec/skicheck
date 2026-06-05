from __future__ import annotations

import cv2
import numpy as np

from .types import BBox


def expand_bbox(box: BBox, frame_shape: tuple[int, int, int], scale: float = 1.4, bottom_bias: float = 0.65) -> BBox:
    height, width = frame_shape[:2]
    pad_w = box.width * (scale - 1.0)
    pad_h = box.height * (scale - 1.0)
    top_pad = pad_h * (1.0 - bottom_bias)
    bottom_pad = pad_h * bottom_bias
    x1 = max(0.0, box.x1 - pad_w / 2.0)
    x2 = min(float(width - 1), box.x2 + pad_w / 2.0)
    y1 = max(0.0, box.y1 - top_pad)
    y2 = min(float(height - 1), box.y2 + bottom_pad)
    return BBox(x1, y1, x2, y2, box.score)


def crop_and_resize(frame: np.ndarray, box: BBox, short_edge: int) -> tuple[np.ndarray, float, float]:
    x1, y1, x2, y2 = [int(round(v)) for v in (box.x1, box.y1, box.x2, box.y2)]
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        raise ValueError("Empty crop")
    h, w = crop.shape[:2]
    scale = max(1.0, float(short_edge) / float(min(h, w)))
    resized = cv2.resize(crop, (int(round(w * scale)), int(round(h * scale))), interpolation=cv2.INTER_CUBIC)
    return resized, w / resized.shape[1], h / resized.shape[0]


def map_keypoints_to_frame(keypoints: np.ndarray, box: BBox, scale_x: float, scale_y: float) -> np.ndarray:
    mapped = keypoints.copy()
    mapped[:, 0] = box.x1 + mapped[:, 0] * scale_x
    mapped[:, 1] = box.y1 + mapped[:, 1] * scale_y
    return mapped

