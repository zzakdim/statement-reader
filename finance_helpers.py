from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class FinancePaths:
    base: Path
    inbox: Path

    @classmethod
    def default(cls) -> "FinancePaths":
        base = Path.home() / "Documents/AI/finance"
        return cls(base=base, inbox=base / "inbox")

    def ensure_output_dir(self) -> None:
        self.base.mkdir(parents=True, exist_ok=True)


def load_activity_frames(inbox: Path) -> pd.DataFrame:
    files = sorted(inbox.glob("activity*.csv"))
    if not files:
        raise FileNotFoundError(f"No activity CSVs found in {inbox}")

    frames = []
    for file_path in files:
        df = pd.read_csv(file_path)
        df["source_file"] = file_path.name
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def normalize_activity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = df["Amount"].astype(float)
    return df


def dedupe_activity(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    dedupe_cols = [
        "Date",
        "Description",
        "Amount",
        "Appears On Your Statement As",
    ]
    before = len(df)
    df = df.drop_duplicates(subset=dedupe_cols)
    after = len(df)
    return df, before - after


def add_year_month(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
    return df


def save_series(series: pd.Series, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    series.to_csv(path)
