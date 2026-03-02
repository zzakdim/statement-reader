"""Workflow CLI for outreach_video_swarm.

Usage examples:
  python tools/run.py new --series quick_tips --topic cold-email-hooks
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from utils import project_root

TEMPLATE_FILES = [
    "brief.md",
    "sources.md",
    "outline.md",
    "script.md",
    "on_screen.txt",
    "metadata.json",
]


def create_video_folder(series_id: str, topic_slug: str) -> Path:
    root = project_root()
    templates_dir = root / "templates"
    videos_dir = root / "videos"

    video_id = f"{series_id}-{topic_slug}"
    destination = videos_dir / video_id

    if destination.exists():
        raise FileExistsError(f"Video folder already exists: {destination}")

    destination.mkdir(parents=True, exist_ok=False)

    for filename in TEMPLATE_FILES:
        source = templates_dir / filename
        if not source.exists():
            raise FileNotFoundError(f"Missing template file: {source}")
        shutil.copy2(source, destination / filename)

    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="outreach_video_swarm workflow tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser(
        "new", help="Create a new video folder and copy template files"
    )
    new_parser.add_argument("--series", required=True, help="Series id (e.g., quick_tips)")
    new_parser.add_argument("--topic", required=True, help="Topic slug (e.g., cold-email-hooks)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "new":
        destination = create_video_folder(args.series, args.topic)
        print(f"Created: {destination}")


if __name__ == "__main__":
    main()
