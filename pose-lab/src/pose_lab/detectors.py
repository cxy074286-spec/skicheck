from __future__ import annotations

import numpy as np

from .types import BBox


class PersonDetector:
    def detect(self, frame: np.ndarray) -> list[BBox]:
        raise NotImplementedError


class UltralyticsPersonDetector(PersonDetector):
    def __init__(self, weights: str, confidence: float = 0.25, person_class_id: int = 0):
        from ultralytics import YOLO

        self.model = YOLO(weights)
        self.confidence = confidence
        self.person_class_id = person_class_id

    def detect(self, frame: np.ndarray) -> list[BBox]:
        result = self.model.predict(frame, conf=self.confidence, verbose=False)[0]
        boxes: list[BBox] = []
        if result.boxes is None:
            return boxes
        xyxy = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        for box, conf, cls in zip(xyxy, confs, classes):
            if cls == self.person_class_id:
                boxes.append(BBox(float(box[0]), float(box[1]), float(box[2]), float(box[3]), float(conf)))
        return boxes


def select_main_person(boxes: list[BBox], frame_shape: tuple[int, int, int]) -> BBox | None:
    if not boxes:
        return None
    height, width = frame_shape[:2]
    center_x, center_y = width / 2.0, height / 2.0

    def score(box: BBox) -> float:
        bx, by = box.center
        center_penalty = abs(bx - center_x) / width + abs(by - center_y) / height
        return box.area * (1.0 + box.score) / (1.0 + center_penalty)

    return max(boxes, key=score)


def build_detector(config: dict) -> PersonDetector:
    backend = config.get("backend", "ultralytics_yolo")
    if backend != "ultralytics_yolo":
        raise ValueError(f"Unsupported detector backend: {backend}")
    return UltralyticsPersonDetector(
        weights=str(config.get("weights", "yolo11n.pt")),
        confidence=float(config.get("confidence", 0.25)),
        person_class_id=int(config.get("person_class_id", 0)),
    )

