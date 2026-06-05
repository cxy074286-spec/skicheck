from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class VideoSpec:
    path: Path
    category: str = "uncategorized"


@dataclass(frozen=True)
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float
    score: float = 0.0

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)


@dataclass
class PoseResult:
    keypoints: np.ndarray
    scores: np.ndarray
    raw: Any = None

    @property
    def has_pose(self) -> bool:
        return self.keypoints.size > 0 and self.scores.size > 0


@dataclass
class FrameResult:
    frame_index: int
    sampled_index: int
    bbox: BBox | None
    expanded_bbox: BBox | None
    pose: PoseResult | None
    core_confidence: float
    valid: bool
    invalid_core: bool
    large_jump: bool

