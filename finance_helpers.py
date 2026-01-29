from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

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


_CHASE_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}(/\d{2,4})?$")


def _parse_chase_amount(raw: str) -> float:
    cleaned = raw.replace(",", "").replace("$", "").strip()
    if not cleaned:
        raise ValueError("Amount was empty")

    is_credit = False
    if cleaned.endswith("CR"):
        is_credit = True
        cleaned = cleaned[:-2].strip()
    if cleaned.startswith("(") and cleaned.endswith(")"):
        is_credit = True
        cleaned = cleaned[1:-1].strip()

    amount = float(cleaned)
    if is_credit:
        amount = -amount
    return amount


def _coerce_chase_date(raw: str, statement_year: int | None) -> str:
    raw = raw.strip()
    if _CHASE_DATE_RE.match(raw):
        if "/" in raw and raw.count("/") == 1 and statement_year is not None:
            return f"{raw}/{statement_year}"
        return raw
    raise ValueError(f"Unsupported date format: {raw}")


def extract_chase_transactions(
    pdf_path: Path,
    *,
    statement_year: int | None = None,
    pages: Iterable[int] | None = None,
) -> pd.DataFrame:
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - depends on optional dep
        raise ImportError(
            "pdfplumber is required to parse Chase PDFs. "
            "Install it with: pip install pdfplumber"
        ) from exc

    rows: list[dict[str, object]] = []
    with pdfplumber.open(pdf_path) as pdf:
        page_iter = (
            (idx, page)
            for idx, page in enumerate(pdf.pages, start=1)
            if pages is None or idx in pages
        )
        for _, page in page_iter:
            tables = page.extract_tables() or []
            for table in tables:
                for row in table:
                    if not row or not row[0]:
                        continue
                    date_raw = str(row[0]).strip()
                    if not _CHASE_DATE_RE.match(date_raw):
                        continue
                    amount_cell = next(
                        (cell for cell in reversed(row) if cell and str(cell).strip()),
                        None,
                    )
                    if not amount_cell:
                        continue
                    description_parts = [
                        str(cell).strip()
                        for cell in row[1:-1]
                        if cell and str(cell).strip()
                    ]
                    description = " ".join(description_parts).strip()
                    if not description:
                        continue
                    try:
                        amount = _parse_chase_amount(str(amount_cell))
                    except ValueError:
                        continue
                    rows.append(
                        {
                            "Date": _coerce_chase_date(date_raw, statement_year),
                            "Description": description,
                            "Amount": amount,
                            "Appears On Your Statement As": description,
                            "Category": "",
                        }
                    )

    return pd.DataFrame(rows)
