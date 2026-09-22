import os
import pandas as pd


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "journal_entries.csv"
)


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("LEDGER VALIDATION")
print("=" * 60)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())


# ------------------------------------------------------------
# 1. Journal ID uniqueness
# ------------------------------------------------------------

duplicate_ids = df["journal_id"].duplicated().sum()

print("\n1. Journal ID uniqueness")
print(f"Duplicate journal IDs: {duplicate_ids}")


# ------------------------------------------------------------
# 2. Missing values
# ------------------------------------------------------------

print("\n2. Missing values")

missing = df.isnull().sum()

print(
    missing[missing > 0].to_string()
    if (missing > 0).any()
    else "No missing values in required fields."
)


# ------------------------------------------------------------
# 3. Amount validation
# ------------------------------------------------------------

print("\n3. Amount validation")

print(f"Minimum amount: {df['amount'].min():,.2f}")
print(f"Maximum amount: {df['amount'].max():,.2f}")

negative_amounts = (df["amount"] < 0).sum()

print(f"Negative amounts: {negative_amounts}")


# ------------------------------------------------------------
# 4. Ground truth
# ------------------------------------------------------------

print("\n4. Ground truth")

print(
    df["is_injected"]
    .value_counts()
    .to_string()
)


# ------------------------------------------------------------
# 5. Anomaly types
# ------------------------------------------------------------

print("\n5. Injected anomaly types")

anomaly_counts = (
    df["anomaly_type"]
    .dropna()
    .str.split("|")
    .explode()
    .value_counts()
)

print(anomaly_counts.to_string())


# ------------------------------------------------------------
# 6. Weekend records
# ------------------------------------------------------------

print("\n6. Weekend records")

df["posting_date"] = pd.to_datetime(
    df["posting_date"]
)

weekend_mask = df["posting_date"].dt.weekday >= 5

print(
    f"Total weekend postings: {weekend_mask.sum():,}"
)

print(
    "Injected weekend postings:",
    (
        weekend_mask
        & df["anomaly_type"]
            .fillna("")
            .str.contains("WEEKEND_POSTING")
    ).sum()
)


# ------------------------------------------------------------
# 7. Same creator / approver
# ------------------------------------------------------------

print("\n7. Same creator and approver")

same_user = (
    df["created_by"] == df["approved_by"]
)

print(f"Total same-user entries: {same_user.sum():,}")

print(
    "Injected same-user entries:",
    (
        same_user
        & df["anomaly_type"]
            .fillna("")
            .str.contains("SAME_CREATOR_APPROVER")
    ).sum()
)


# ------------------------------------------------------------
# 8. Near approval limit
# ------------------------------------------------------------

print("\n8. Near approval limit")

near_limit = (
    (df["amount"] >= 95_000)
    & (df["amount"] < 100_000)
)

print(
    f"Entries between ₹95,000 and ₹99,999.99: "
    f"{near_limit.sum():,}"
)

print(
    "Injected near-limit entries:",
    (
        near_limit
        & df["anomaly_type"]
            .fillna("")
            .str.contains("NEAR_APPROVAL_LIMIT")
    ).sum()
)


# ------------------------------------------------------------
# 9. Round amounts
# ------------------------------------------------------------

print("\n9. Round amounts")

round_amount = (
    df["amount"] % 1000 == 0
)

print(
    f"Amounts divisible by ₹1,000: "
    f"{round_amount.sum():,}"
)

print(
    "Injected round-amount entries:",
    (
        round_amount
        & df["anomaly_type"]
            .fillna("")
            .str.contains("ROUND_AMOUNT")
    ).sum()
)


# ------------------------------------------------------------
# Final result
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)