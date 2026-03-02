"""Shared utility helpers for scripts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict[str, Any]:
    command = [
        "ruby",
        "-rjson",
        "-ryaml",
        "-e",
        "puts JSON.dump(YAML.safe_load(File.read(ARGV[0]), aliases: true) || {})",
        str(path),
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Ruby is required for YAML loading but was not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise ValueError(f"Invalid YAML in {path}: {details}") from exc

    data = json.loads(result.stdout or "{}")
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping in {path}")
    return data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict[str, Any]:
    root = project_root()
    config_dir = root / "channel_config"
    files = [
        config_dir / "channel_config.yaml",
        config_dir / "constraints.yaml",
        config_dir / "runtime.yaml",
    ]

    merged: dict[str, Any] = {}
    for file_path in files:
        merged = _deep_merge(merged, _load_yaml(file_path))

    return merged
