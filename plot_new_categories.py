import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

BASE = Path.home() / "Documents/AI/finance"
df = pd.read_csv(BASE / "combined_with_new_categories.csv")

# Parse dates
df["Date"] = pd.to_datetime(df["Date"])
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

# -------------------------
# 1) Total spend by category
# -------------------------
by_cat = (
    df.groupby("NewCategory")["Amount"]
      .sum()
      .sort_values()
)

plt.figure(figsize=(10, 6))
by_cat.plot(kind="barh")
plt.title("Total Spend by Category")
plt.xlabel("Amount")
plt.tight_layout()
plt.savefig(BASE / "new_spend_by_category.png")
plt.close()

# -------------------------
# 2) Monthly Fixed vs Variable
# -------------------------
fixed_var = (
    df.groupby(["YearMonth", "SpendType"])["Amount"]
      .sum()
      .unstack(fill_value=0)
      .sort_index()
)

fixed_var.plot(kind="bar", stacked=True, figsize=(12, 7))
plt.title("Monthly Spend: Fixed vs Variable")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.tight_layout()
plt.savefig(BASE / "monthly_fixed_vs_variable.png")
plt.close()

# -------------------------
# 3) Variable spend trend (this is the lever)
# -------------------------
variable_only = (
    df[df["SpendType"] == "Variable"]
    .groupby("YearMonth")["Amount"]
    .sum()
    .sort_index()
)

plt.figure(figsize=(10, 6))
variable_only.plot(kind="line", marker="o")
plt.title("Monthly Variable Spend Trend")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.tight_layout()
plt.savefig(BASE / "variable_spend_trend.png")
plt.close()

print("Graphs written to", BASE)
