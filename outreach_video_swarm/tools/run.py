"""Workflow CLI for outreach_video_swarm.

Usage examples:
  python tools/run.py new --series quick_tips --topic cold-email-hooks
  python tools/run.py meta quick_tips-cold-email-hooks
"""

from __future__ import annotations

import argparse
import json
import re
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


def _section_text(markdown_text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    lines = markdown_text.splitlines()

    start = None
    for index, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            start = index + 1
            break

    if start is None:
        return ""

    collected: list[str] = []
    for line in lines[start:]:
        if line.strip().startswith("## "):
            break
        cleaned = line.strip().lstrip("- ").strip()
        if cleaned:
            collected.append(cleaned)

    return " ".join(collected).strip()


def _extract_key_points(brief_text: str) -> list[str]:
    lines = brief_text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "## Key Points (3 max)":
            start = index + 1
            break

    if start is None:
        return []

    section_lines: list[str] = []
    for line in lines[start:]:
        if line.strip().startswith("## "):
            break
        section_lines.append(line.rstrip())

    points: list[str] = []
    for line in section_lines:
        match = re.match(r"^\s*\d+\.\s*(.+?)\s*$", line)
        if match:
            value = match.group(1).strip()
            if value:
                points.append(value)

    if points:
        return points

    fallback = " ".join(line.strip().lstrip("- ") for line in section_lines if line.strip())
    return [part.strip() for part in fallback.split(";") if part.strip()]


def _series_from_video_folder(video_folder_name: str) -> str:
    if "-" in video_folder_name:
        return video_folder_name.split("-", 1)[0]
    return "quick_tips"


def _topic_from_video_folder(video_folder_name: str) -> str:
    if "-" in video_folder_name:
        return video_folder_name.split("-", 1)[1].replace("-", " ").strip().title()
    return video_folder_name.replace("-", " ").strip().title()


def generate_metadata(video_folder: str) -> Path:
    root = project_root()
    video_path = Path(video_folder)
    if not video_path.is_absolute():
        video_path = root / "videos" / video_folder

    if not video_path.exists():
        raise FileNotFoundError(f"Video folder does not exist: {video_path}")

    brief_path = video_path / "brief.md"
    outline_path = video_path / "outline.md"
    metadata_path = video_path / "metadata.json"

    if not brief_path.exists():
        raise FileNotFoundError(f"brief.md not found: {brief_path}")
    if not outline_path.exists():
        raise FileNotFoundError(f"outline.md not found: {outline_path}")

    brief_text = brief_path.read_text(encoding="utf-8")
    outline_text = outline_path.read_text(encoding="utf-8")

    working_title = _section_text(brief_text, "Working Title")
    goal = _section_text(brief_text, "Goal")
    core_message = _section_text(brief_text, "Core Message")
    key_points = _extract_key_points(brief_text)
    hook = _section_text(outline_text, "Hook (0-10s)")
    cta = _section_text(outline_text, "CTA + Close (final 10-15s)")

    fallback_topic = _topic_from_video_folder(video_path.name)
    title = working_title or f"{fallback_topic} | Quick Guide"

    description_parts = [part for part in [goal, core_message, f"CTA: {cta}" if cta else ""] if part]
    description = " ".join(description_parts) or "Short practical video based on brief and outline."

    tags = [
        tag.lower().replace(" ", "-")
        for tag in [video_path.name, _series_from_video_folder(video_path.name), *key_points[:2]]
        if tag
    ]

    metadata = {
        "title": title,
        "description": description,
        "tags": tags,
        "series_id": _series_from_video_folder(video_path.name),
        "language": "en",
        "thumbnail_text": (hook or fallback_topic)[:60],
        "publish": {
            "status": "draft",
            "scheduled_at": "YYYY-MM-DDTHH:MM:SSZ",
        },
    }

    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="outreach_video_swarm workflow tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser(
        "new", help="Create a new video folder and copy template files"
    )
    new_parser.add_argument("--series", required=True, help="Series id (e.g., quick_tips)")
    new_parser.add_argument("--topic", required=True, help="Topic slug (e.g., cold-email-hooks)")

    meta_parser = subparsers.add_parser(
        "meta", help="Generate metadata.json from brief.md and outline.md"
    )
    meta_parser.add_argument(
        "video_folder",
        help="Video folder name under videos/ (or absolute/relative path)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "new":
            destination = create_video_folder(args.series, args.topic)
            print(f"Created: {destination}")
        elif args.command == "meta":
            metadata_path = generate_metadata(args.video_folder)
            print(f"Updated: {metadata_path}")
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    main()
