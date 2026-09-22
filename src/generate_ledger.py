import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
TOTAL_RECORDS = 50_000

# Five anomaly categories
ANOMALIES_PER_TYPE = 150

APPROVAL_LIMIT = 100_000

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "journal_entries.csv")


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)

fake = Faker()
fake.seed_instance(SEED)


# ============================================================
# MASTER DATA
# ============================================================

ACCOUNTS = [
    ("1000", "Cash"),
    ("1100", "Accounts Receivable"),
    ("1200", "Inventory"),
    ("1300", "Prepaid Expenses"),
    ("2000", "Accounts Payable"),
    ("2100", "Accrued Expenses"),
    ("3000", "Common Stock"),
    ("4000", "Sales Revenue"),
    ("4100", "Service Revenue"),
    ("5000", "Cost of Goods Sold"),
    ("6000", "Salaries Expense"),
    ("6100", "Rent Expense"),
    ("6200", "Utilities Expense"),
    ("6300", "Office Supplies"),
    ("6400", "Travel Expense"),
    ("6500", "Professional Services"),
]

USERS = [f"USER_{i:03d}" for i in range(1, 51)]

SOURCE_SYSTEMS = [
    "SAP",
    "Oracle",
    "Manual",
    "Legacy"
]

DESCRIPTIONS = [
    "Monthly operating expense",
    "Office supplies purchase",
    "Vendor payment",
    "Customer receipt",
    "Payroll adjustment",
    "Utility payment",
    "Travel expense",
    "Professional service fee",
    "Inventory adjustment",
    "Rent payment",
    "Insurance expense",
    "Maintenance expense",
    "Revenue adjustment",
    "Accrual entry",
    "Reclassification entry",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_datetime(start_date, end_date):
    """
    Generate a random datetime between two dates.
    """
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)


def random_amount():
    """
    Generate a realistic transaction amount.
    Most transactions remain below the approval threshold.
    """
    amount = np.random.lognormal(mean=9.2, sigma=1.0)

    # Keep the majority of normal transactions below the limit.
    amount = min(amount, 95_000)

    return round(float(amount), 2)


def choose_account():
    return random.choice(ACCOUNTS)


def choose_users():
    """
    Normally creator and approver are different people.
    """
    creator = random.choice(USERS)

    approver_candidates = [u for u in USERS if u != creator]
    approver = random.choice(approver_candidates)

    return creator, approver


def generate_normal_entry(journal_id, start_date, end_date):
    """
    Generate one ordinary journal entry.
    """

    account_code, account_name = choose_account()

    # Most normal journal entries occur on weekdays.
    # A small percentage occur legitimately on weekends.

    if random.random() < 0.05:

        # Legitimate weekend posting
        while True:
            posting_datetime = random_datetime(
                start_date,
                end_date
            )

            if posting_datetime.weekday() >= 5:
                break

    else:

        # Normal weekday posting
        while True:
            posting_datetime = random_datetime(
                start_date,
                end_date
            )

            if posting_datetime.weekday() < 5:
                break

    creator, approver = choose_users()

    created_timestamp = posting_datetime - timedelta(
        minutes=random.randint(5, 1440)
    )

    approval_timestamp = posting_datetime + timedelta(
        minutes=random.randint(5, 1440)
    )

    return {
        "journal_id": journal_id,
        "posting_date": posting_datetime.date(),
        "account_code": account_code,
        "account_name": account_name,
        "amount": random_amount(),
        "description": random.choice(DESCRIPTIONS),
        "source_system": random.choice(SOURCE_SYSTEMS),
        "created_by": creator,
        "approved_by": approver,
        "created_timestamp": created_timestamp,
        "approval_timestamp": approval_timestamp,

        # Ground truth
        "is_injected": False,
        "anomaly_type": None,
    }


# ============================================================
# GENERATE BASE DATA
# ============================================================

print("Generating base ledger...")

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 8, 31)

records = []

for i in range(1, TOTAL_RECORDS + 1):

    journal_id = f"JE{i:06d}"

    record = generate_normal_entry(
        journal_id,
        START_DATE,
        END_DATE
    )

    records.append(record)


df = pd.DataFrame(records)

print(f"Base records generated: {len(df):,}")


# ============================================================
# ANOMALY INJECTION
# ============================================================

print("Injecting anomalies...")

# ============================================================
# RESERVE DISJOINT INDICES FOR EACH ANOMALY TYPE
# ============================================================

available_indices = list(df.index)

random.shuffle(available_indices)

weekend_indices = available_indices[
    0:ANOMALIES_PER_TYPE
]

round_indices = available_indices[
    ANOMALIES_PER_TYPE:ANOMALIES_PER_TYPE * 2
]

near_limit_indices = available_indices[
    ANOMALIES_PER_TYPE * 2:ANOMALIES_PER_TYPE * 3
]

same_user_indices = available_indices[
    ANOMALIES_PER_TYPE * 3:ANOMALIES_PER_TYPE * 4
]

duplicate_source_indices = available_indices[
    ANOMALIES_PER_TYPE * 4:ANOMALIES_PER_TYPE * 5
]

# ------------------------------------------------------------
# 1. WEEKEND POSTINGS
# ------------------------------------------------------------



for idx in weekend_indices:

    # Find a Saturday or Sunday
    while True:
        date = START_DATE + timedelta(
            days=random.randint(
                0,
                (END_DATE - START_DATE).days
            )
        )

        if date.weekday() >= 5:
            break

    df.loc[idx, "posting_date"] = date.date()
    df.loc[idx, "is_injected"] = True

    existing = df.loc[idx, "anomaly_type"]

    if pd.isna(existing):
        df.loc[idx, "anomaly_type"] = "WEEKEND_POSTING"
    else:
        df.loc[idx, "anomaly_type"] = (
            f"{existing}|WEEKEND_POSTING"
        )


# ------------------------------------------------------------
# 2. ROUND AMOUNTS
# ------------------------------------------------------------



round_values = [
    10_000,
    25_000,
    50_000,
    75_000,
    100_000,
    150_000,
    250_000,
]

for idx in round_indices:

    df.loc[idx, "amount"] = random.choice(round_values)
    df.loc[idx, "is_injected"] = True

    existing = df.loc[idx, "anomaly_type"]

    if pd.isna(existing):
        df.loc[idx, "anomaly_type"] = "ROUND_AMOUNT"
    else:
        df.loc[idx, "anomaly_type"] = (
            f"{existing}|ROUND_AMOUNT"
        )


# ------------------------------------------------------------
# 3. NEAR APPROVAL LIMIT
# ------------------------------------------------------------



for idx in near_limit_indices:

    # Deliberately below the approval threshold
    amount = random.choice([
        95_000,
        97_500,
        98_000,
        98_500,
        99_000,
        99_500,
        99_900,
        99_950,
        99_999,
    ])

    df.loc[idx, "amount"] = amount
    df.loc[idx, "is_injected"] = True

    existing = df.loc[idx, "anomaly_type"]

    if pd.isna(existing):
        df.loc[idx, "anomaly_type"] = "NEAR_APPROVAL_LIMIT"
    else:
        df.loc[idx, "anomaly_type"] = (
            f"{existing}|NEAR_APPROVAL_LIMIT"
        )


# ------------------------------------------------------------
# 4. SAME CREATOR AND APPROVER
# ------------------------------------------------------------



for idx in same_user_indices:

    user = random.choice(USERS)

    df.loc[idx, "created_by"] = user
    df.loc[idx, "approved_by"] = user
    df.loc[idx, "is_injected"] = True

    existing = df.loc[idx, "anomaly_type"]

    if pd.isna(existing):
        df.loc[idx, "anomaly_type"] = "SAME_CREATOR_APPROVER"
    else:
        df.loc[idx, "anomaly_type"] = (
            f"{existing}|SAME_CREATOR_APPROVER"
        )


# ------------------------------------------------------------
# 5. DUPLICATE TRANSACTIONS
# ------------------------------------------------------------



duplicate_rows = []

next_duplicate_number = TOTAL_RECORDS + 1

for idx in duplicate_source_indices:

    source = df.loc[idx].copy()

    duplicate = source.copy()

    duplicate["journal_id"] = (
        f"JE{next_duplicate_number:06d}"
    )

    next_duplicate_number += 1

    # Keep the important transaction characteristics identical.
    # This creates a duplicate with a different journal ID.
    duplicate["is_injected"] = True

    existing = duplicate["anomaly_type"]

    if pd.isna(existing):
        duplicate["anomaly_type"] = "DUPLICATE"
    else:
        duplicate["anomaly_type"] = (
            f"{existing}|DUPLICATE"
        )

    duplicate_rows.append(duplicate)

    # Mark the original transaction as part of the injected case.
    df.loc[idx, "is_injected"] = True

    existing_original = df.loc[idx, "anomaly_type"]

    if pd.isna(existing_original):
        df.loc[idx, "anomaly_type"] = "DUPLICATE"
    elif "DUPLICATE" not in str(existing_original):
        df.loc[idx, "anomaly_type"] = (
            f"{existing_original}|DUPLICATE"
        )


duplicate_df = pd.DataFrame(duplicate_rows)

df = pd.concat(
    [df, duplicate_df],
    ignore_index=True
)


# ============================================================
# LEGITIMATE LOOK-ALIKE TRANSACTIONS
# ============================================================

print("Adding legitimate look-alikes...")

lookalike_records = []


# ------------------------------------------------------------
# Legitimate weekend postings
# ------------------------------------------------------------

for _ in range(20):

    while True:
        date = START_DATE + timedelta(
            days=random.randint(
                0,
                (END_DATE - START_DATE).days
            )
        )

        if date.weekday() >= 5:
            break

    record = generate_normal_entry(
        f"TEMP_{len(lookalike_records):05d}",
        START_DATE,
        END_DATE
    )

    record["posting_date"] = date.date()

    lookalike_records.append(record)


# ------------------------------------------------------------
# Legitimate round amounts
# ------------------------------------------------------------

legitimate_round_transactions = [
    (50_000, "Monthly office rent"),
    (100_000, "Insurance payment"),
    (250_000, "Annual facility contract"),
    (75_000, "Quarterly maintenance payment"),
    (25_000, "Monthly software subscription"),
]

for amount, description in legitimate_round_transactions:

    record = generate_normal_entry(
        f"TEMP_{len(lookalike_records):05d}",
        START_DATE,
        END_DATE
    )

    record["amount"] = amount
    record["description"] = description

    lookalike_records.append(record)


# ------------------------------------------------------------
# Legitimate near-limit transactions
# ------------------------------------------------------------

for amount in [99_500, 99_800, 99_999]:

    record = generate_normal_entry(
        f"TEMP_{len(lookalike_records):05d}",
        START_DATE,
        END_DATE
    )

    record["amount"] = amount
    record["description"] = "Approved recurring contract"

    lookalike_records.append(record)


# Add legitimate look-alikes
lookalike_df = pd.DataFrame(lookalike_records)

df = pd.concat(
    [df, lookalike_df],
    ignore_index=True
)


# ============================================================
# FIX JOURNAL IDS
# ============================================================

# Replace temporary IDs with proper unique IDs.
used_ids = set()

for idx in df.index:

    journal_id = df.loc[idx, "journal_id"]

    if str(journal_id).startswith("TEMP_"):

        new_id = f"JE{len(df) + idx + 1:06d}"

        while new_id in used_ids:
            new_id = f"JE{random.randint(1, 999999):06d}"

        df.loc[idx, "journal_id"] = new_id

    used_ids.add(df.loc[idx, "journal_id"])


# ============================================================
# SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=SEED
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("LEDGER GENERATION COMPLETE")
print("=" * 60)

print(f"Output file : {OUTPUT_FILE}")
print(f"Total rows  : {len(df):,}")

print()
print("Ground-truth injected rows:")
print(
    df["is_injected"]
    .value_counts()
    .to_string()
)

print()
print("Anomaly types:")
print(
    df["anomaly_type"]
    .dropna()
    .str.split("|")
    .explode()
    .value_counts()
    .to_string()
)

print()
print("Sample:")
print(
    df.head(10).to_string(index=False)
)