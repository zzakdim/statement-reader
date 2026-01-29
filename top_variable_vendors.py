import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

BASE = Path.home() / "Documents/AI/finance"
df = pd.read_csv(BASE / "combined_with_new_categories.csv")

# Only variable spend
df = df[df["SpendType"] == "Variable"]

# Group by vendor
vendor = (
    df.groupby("Description")["Amount"]
      .sum()
      .sort_values(ascending=False)
)

TOP_N = 12
top = vendor.head(TOP_N)
other = vendor.iloc[TOP_N:].sum()

plot_data = top.copy()
plot_data["Other"] = other

# Save table
out_csv = BASE / "top_variable_vendors.csv"
plot_data.to_csv(out_csv)

# Plot
plt.figure(figsize=(10, 6))
plot_data.sort_values().plot(kind="barh")
plt.title("Top Variable Spend by Vendor")
plt.xlabel("Amount")
plt.tight_layout()
plt.savefig(BASE / "top_variable_vendors.png")
plt.close()

print("Wrote:", out_csv)
print("Wrote:", BASE / "top_variable_vendors.png")
