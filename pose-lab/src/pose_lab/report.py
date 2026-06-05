from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def collect_metrics(run_dir: Path) -> pd.DataFrame:
    rows = []
    for metrics_path in sorted(run_dir.glob("*/*/metrics.json")):
        with metrics_path.open("r", encoding="utf-8") as handle:
            row = json.load(handle)
        row["metrics_path"] = str(metrics_path)
        rows.append(row)
    return pd.DataFrame(rows)


def write_report(run_dir: Path) -> Path:
    df = collect_metrics(run_dir)
    report_path = run_dir / "summary.md"
    if df.empty:
        report_path.write_text("# Pose Lab Summary\n\nNo metrics found.\n", encoding="utf-8")
        return report_path

    by_model = (
        df.groupby("model", as_index=False)
        .agg(
            videos=("video_name", "count"),
            sampled_frames=("sampled_frames", "sum"),
            valid_pose_frames=("valid_pose_frames", "sum"),
            valid_pose_ratio=("valid_pose_ratio", "mean"),
            invalid_core_joint_frames=("invalid_core_joint_frames", "sum"),
            large_joint_jump_frames=("large_joint_jump_frames", "sum"),
            processing_seconds=("processing_seconds", "sum"),
            average_core_joint_confidence=("average_core_joint_confidence", "mean"),
        )
        .sort_values(["valid_pose_ratio", "average_core_joint_confidence"], ascending=False)
    )

    lines = [
        "# Pose Lab Summary",
        "",
        "## Model Results",
        "",
        by_model.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Per Video Results",
        "",
        df[
            [
                "model",
                "video_name",
                "sampled_frames",
                "valid_pose_frames",
                "valid_pose_ratio",
                "invalid_core_joint_frames",
                "large_joint_jump_frames",
                "processing_seconds",
                "average_core_joint_confidence",
            ]
        ].to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Screenshot Checklist",
        "",
        "- Typical success frames: choose high-confidence `sample_frames/*_ok_*` from the top models.",
        "- Typical failure frames: choose red `sample_frames/*_bad_*` and inspect `anomaly_frames.json`.",
        "",
        "## Recommendation Template",
        "",
        "- Frontend model:",
        "- Backend full-video analysis model:",
        "- Fine-tuning recommendation:",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    df.to_csv(run_dir / "metrics.csv", index=False, encoding="utf-8")
    by_model.to_csv(run_dir / "model_summary.csv", index=False, encoding="utf-8")
    return report_path

