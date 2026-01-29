from pathlib import Path

import pandas as pd

from finance_helpers import FinancePaths

PATHS = FinancePaths.default()
df = pd.read_csv(PATHS.base / "combined_clean.csv")

# Merge rules from Qwen (cleaned)
MERGE_RULES = {
    "Merchandise & Supplies-Department Stores": "Shopping",
    "Merchandise & Supplies-Wholesale Stores": "Shopping",
    "Merchandise & Supplies-Pharmacies": "Healthcare",
    "Business Services-Internet Services": "Internet & Communications",
    "Business Services-Office Supplies": "Shopping",
    "Transportation-Rail Services": "Transportation",
    "Restaurant-Restaurant": "Restaurants",
    "Other-Government Services": "Taxes & Fines"
}

# Fixed vs Variable classification
FIXED_VARIABLE = {
    "Groceries": "Variable",
    "Restaurants": "Variable",
    "Utilities": "Fixed",
    "Internet & Communications": "Fixed",
    "Transportation": "Variable",
    "Shopping": "Variable",
    "Entertainment": "Variable",
    "Healthcare": "Fixed",
    "Insurance": "Fixed",
    "Taxes & Fines": "Fixed",
    "Other": "Variable"
}

# Start with Amex category
df["NewCategory"] = df["Category"]

# Apply merge rules
df["NewCategory"] = df["NewCategory"].replace(MERGE_RULES)

# Fill unknowns
df["NewCategory"] = df["NewCategory"].fillna("Other")

# Assign Fixed / Variable
df["SpendType"] = df["NewCategory"].map(FIXED_VARIABLE).fillna("Variable")

# Save result
out = PATHS.base / "combined_with_new_categories.csv"
df.to_csv(out, index=False)

print("Wrote:", out)
