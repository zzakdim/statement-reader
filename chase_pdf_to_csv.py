from __future__ import annotations

from pathlib import Path

from finance_helpers import FinancePaths, extract_chase_transactions

PATHS = FinancePaths.default()
PATHS.ensure_output_dir()

# Set this if your Chase statement PDF only includes MM/DD dates without a year.
STATEMENT_YEAR: int | None = None

pdf_files = sorted(PATHS.inbox.glob("chase*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No Chase PDFs found in {PATHS.inbox}")

for pdf_path in pdf_files:
    df = extract_chase_transactions(pdf_path, statement_year=STATEMENT_YEAR)
    if df.empty:
        print(f"No transactions found in {pdf_path.name}")
        continue

    out_name = f"activity_{pdf_path.stem}.csv"
    out_path = PATHS.inbox / out_name
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
