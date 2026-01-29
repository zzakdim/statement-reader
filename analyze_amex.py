from pathlib import Path
import matplotlib.pyplot as plt

from finance_helpers import (
    FinancePaths,
    add_year_month,
    dedupe_activity,
    load_activity_frames,
    normalize_activity,
)

PATHS = FinancePaths.default()
PATHS.ensure_output_dir()

df = load_activity_frames(PATHS.inbox)
df = normalize_activity(df)

df, removed = dedupe_activity(df)
print(f"Removed {removed} duplicate rows")

# Add Year-Month for grouping
df = add_year_month(df)

# Save combined clean file
combined_path = PATHS.base / "combined_clean.csv"
df.to_csv(combined_path, index=False)

# Aggregate by category
by_category = (
    df.groupby("Category", dropna=False)["Amount"]
      .sum()
      .sort_values()
)

by_category_path = PATHS.base / "by_category.csv"
by_category.to_csv(by_category_path)

# Aggregate by month
by_month = (
    df.groupby("YearMonth")["Amount"]
      .sum()
      .sort_index()
)

by_month_path = PATHS.base / "by_month.csv"
by_month.to_csv(by_month_path)

# ---- Graphs ----

# Spend by category
plt.figure(figsize=(10, 6))
by_category.plot(kind="barh")
plt.title("Total Spend by Category")
plt.xlabel("Amount")
plt.tight_layout()
plt.savefig(PATHS.base / "spend_by_category.png")
plt.close()

# Monthly total spend
plt.figure(figsize=(10, 6))
by_month.plot(kind="line", marker="o")
plt.title("Monthly Total Spend")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.tight_layout()
plt.savefig(PATHS.base / "monthly_spend.png")
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
plt.savefig(PATHS.base / "monthly_category_stacked.png")
plt.close()

print("Outputs written to:", PATHS.base)
