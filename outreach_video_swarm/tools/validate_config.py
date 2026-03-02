"""Validate YAML config files and required runtime keys."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from outreach_video_swarm.tools.utils import load_config, project_root

REQUIRED_KEYS: dict[str, type] = {
    "channel": dict,
    "publishing": dict,
    "branding": dict,
    "editorial": dict,
    "video": dict,
    "audio": dict,
    "assets": dict,
    "render": dict,
    "experiments": dict,
    "upload": dict,
}

REQUIRED_NESTED: dict[str, type] = {
    "render.seconds_per_slide_default": (int, float),
    "render.target_length_range_seconds": dict,
    "render.target_length_range_seconds.min": int,
    "render.target_length_range_seconds.max": int,
    "render.music_ducking_db": (int, float),
    "experiments.explore_ratio": (int, float),
    "upload.privacy_default": str,
    "video.fps": int,
    "video.resolution": str,
}


def _get_path(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted_key)
        current = current[part]
    return current


def _type_name(value_type: type | tuple[type, ...]) -> str:
    if isinstance(value_type, tuple):
        return " or ".join(t.__name__ for t in value_type)
    return value_type.__name__


def validate_config() -> dict[str, Any]:
    config = load_config()
    errors: list[str] = []

    for key, expected_type in REQUIRED_KEYS.items():
        value = config.get(key)
        if value is None:
            errors.append(f"Missing required key: {key}")
        elif not isinstance(value, expected_type):
            errors.append(
                f"Invalid type for '{key}': expected {expected_type.__name__}, got {type(value).__name__}"
            )

    for dotted_key, expected_type in REQUIRED_NESTED.items():
        try:
            value = _get_path(config, dotted_key)
        except KeyError:
            errors.append(f"Missing required key: {dotted_key}")
            continue

        if not isinstance(value, expected_type):
            errors.append(
                f"Invalid type for '{dotted_key}': expected {_type_name(expected_type)}, got {type(value).__name__}"
            )

    try:
        min_seconds = _get_path(config, "render.target_length_range_seconds.min")
        max_seconds = _get_path(config, "render.target_length_range_seconds.max")
        if min_seconds > max_seconds:
            errors.append("render.target_length_range_seconds.min must be <= max")
    except KeyError:
        pass

    if errors:
        raise ValueError("; ".join(errors))

    return config


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Validate outreach_video_swarm config files")


def main() -> None:
    parser = build_parser()
    parser.parse_args()

    try:
        validate_config()
        root = project_root()
        print(f"OK: {root / 'channel_config' / 'channel_config.yaml'}")
        print(f"OK: {root / 'channel_config' / 'constraints.yaml'}")
        print(f"OK: {root / 'channel_config' / 'runtime.yaml'}")
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    main()
