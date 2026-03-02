"""Validate YAML config files under channel_config/."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from outreach_video_swarm.tools.utils import project_root


def validate_yaml_file(path: Path) -> None:
    command = [
        "ruby",
        "-e",
        "require 'yaml'; YAML.safe_load(File.read(ARGV[0]), aliases: true)",
        str(path),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Ruby is required for YAML validation but was not found on PATH"
        ) from exc
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise ValueError(f"Invalid YAML in {path}: {details}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate outreach_video_swarm YAML config files")
    parser.add_argument(
        "--files",
        nargs="*",
        default=[
            "channel_config/channel_config.yaml",
            "channel_config/constraints.yaml",
        ],
        help="Config files relative to outreach_video_swarm root",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    root = project_root()

    try:
        for rel in args.files:
            file_path = root / rel
            if not file_path.exists():
                raise FileNotFoundError(f"Config file not found: {file_path}")
            validate_yaml_file(file_path)
            print(f"OK: {file_path}")
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    main()
