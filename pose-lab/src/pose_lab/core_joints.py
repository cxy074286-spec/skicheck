from __future__ import annotations


CORE_LAYOUTS: dict[str, list[int]] = {
    "mediapipe33": [11, 12, 23, 24, 25, 26, 27, 28, 31, 32],
    "coco17": [5, 6, 11, 12, 13, 14, 15, 16],
    "halpe26": [5, 6, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25],
}

SKELETONS: dict[str, list[tuple[int, int]]] = {
    "mediapipe33": [
        (11, 12), (11, 23), (12, 24), (23, 24),
        (11, 13), (13, 15), (12, 14), (14, 16),
        (23, 25), (25, 27), (27, 31), (24, 26), (26, 28), (28, 32),
    ],
    "coco17": [
        (5, 6), (5, 11), (6, 12), (11, 12),
        (5, 7), (7, 9), (6, 8), (8, 10),
        (11, 13), (13, 15), (12, 14), (14, 16),
    ],
    "halpe26": [
        (5, 6), (5, 11), (6, 12), (11, 12),
        (5, 7), (7, 9), (6, 8), (8, 10),
        (11, 13), (13, 15), (12, 14), (14, 16),
        (15, 20), (15, 22), (15, 24), (16, 21), (16, 23), (16, 25),
    ],
}


def core_indices(layout: str) -> list[int]:
    if layout not in CORE_LAYOUTS:
        raise KeyError(f"Unknown core layout: {layout}")
    return CORE_LAYOUTS[layout]


def skeleton_edges(layout: str) -> list[tuple[int, int]]:
    return SKELETONS.get(layout, [])

