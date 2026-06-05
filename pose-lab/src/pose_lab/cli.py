from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="SkiCheck pose model validation lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run pose validation")
    run_parser.add_argument("--config", type=Path, default=Path("configs/models.yaml"))
    run_parser.add_argument("--manifest", type=Path, required=True)
    run_parser.add_argument("--out", type=Path, default=Path("runs/exp01"))
    run_parser.add_argument("--models", type=str, default="", help="Comma-separated model ids. Empty means all.")

    report_parser = subparsers.add_parser("report", help="Generate Markdown/CSV report from metrics")
    report_parser.add_argument("--run", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "run":
        from .config import load_video_manifest
        from .runner import run_experiment

        videos = load_video_manifest(args.manifest)
        selected = [item.strip() for item in args.models.split(",") if item.strip()] or None
        run_experiment(args.config, videos, args.out, selected)
    elif args.command == "report":
        from .report import write_report

        report_path = write_report(args.run)
        print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
