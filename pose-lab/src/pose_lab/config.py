from __future__ import annotations

from pathlib import Path

import yaml

from .types import VideoSpec


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_video_manifest(path: Path) -> list[VideoSpec]:
    data = load_yaml(path)
    videos = data.get("videos", [])
    if not isinstance(videos, list):
        raise ValueError("Manifest field 'videos' must be a list")
    specs: list[VideoSpec] = []
    for item in videos:
        if isinstance(item, str):
            specs.append(VideoSpec(Path(item)))
        elif isinstance(item, dict) and "path" in item:
            specs.append(VideoSpec(Path(item["path"]), str(item.get("category", "uncategorized"))))
        else:
            raise ValueError(f"Invalid video entry: {item!r}")
    return specs

