import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Paths
INBOX = Path.home() / "Documents/AI/finance/inbox"
OUT = Path.home() / "Documents/AI/finance"
OUT.mkdir(exist_ok=True)

# Load all activity CSVs
files = sorted(INBOX.glob("activity*.csv"))
dfs = []

for f in files:
    df = pd.read_csv(f)
    df["source_file"] = f.name
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

# Normalize columns
df["Date"] = pd.to_datetime(df["Date"])
df["Amount"] = df["Amount"].astype(float)

# Safe deduplication key
dedupe_cols = [
    "Date",
    "Description",
    "Amount",
    "Appears On Your Statement As"
]

before = len(df)
df = df.drop_duplicates(subset=dedupe_cols)
after = len(df)

print(f"Removed {before - after} duplicate rows")

# Add Year-Month for grouping
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

# Save combined clean file
combined_path = OUT / "combined_clean.csv"
df.to_csv(combined_path, index=False)

# Aggregate by category
by_category = (
    df.groupby("Category", dropna=False)["Amount"]
      .sum()
      .sort_values()
)

by_category_path = OUT / "by_category.csv"
by_category.to_csv(by_category_path)

# Aggregate by month
by_month = (
    df.groupby("YearMonth")["Amount"]
      .sum()
      .sort_index()
)

by_month_path = OUT / "by_month.csv"
by_month.to_csv(by_month_path)

# ---- Graphs ----

# Spend by category
plt.figure(figsize=(10, 6))
by_category.plot(kind="barh")
plt.title("Total Spend by Category")
plt.xlabel("Amount")
plt.tight_layout()
plt.savefig(OUT / "spend_by_category.png")
plt.close()

# Monthly total spend
plt.figure(figsize=(10, 6))
by_month.plot(kind="line", marker="o")
plt.title("Monthly Total Spend")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.tight_layout()
plt.savefig(OUT / "monthly_spend.png")
plt.close()

# Monthly stacked category spend
pivot = (
    df.pivot_table(
        index="YearMonth",
        columns="Category",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    )
    .sort_index()
)

pivot.plot(kind="bar", stacked=True, figsize=(12, 7))
plt.title("Monthly Spend by Category")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.tight_layout()
plt.savefig(OUT / "monthly_category_stacked.png")
plt.close()

print("Outputs written to:", OUT)
