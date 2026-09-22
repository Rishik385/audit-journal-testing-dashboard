
import os
import pandas as pd
import mysql.connector

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(PROJECT_ROOT, "data", "journal_entries.csv")

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": input("Enter MySQL root password: "),
    "database": "audit_analytics"
}

print("Reading CSV...")

df = pd.read_csv(CSV_FILE)

df["anomaly_type"] = df["anomaly_type"].where(
    df["anomaly_type"].notna(), None
)

print(f"Rows loaded from CSV: {len(df):,}")

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()

print("Connected to MySQL.")

cursor.execute("DELETE FROM journal_entries")
connection.commit()

insert_query = """
INSERT INTO journal_entries (
    journal_id,
    posting_date,
    account_code,
    account_name,
    amount,
    description,
    source_system,
    created_by,
    approved_by,
    created_timestamp,
    approval_timestamp,
    is_injected,
    anomaly_type
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

columns = [
    "journal_id",
    "posting_date",
    "account_code",
    "account_name",
    "amount",
    "description",
    "source_system",
    "created_by",
    "approved_by",
    "created_timestamp",
    "approval_timestamp",
    "is_injected",
    "anomaly_type"
]

data = []

for _, row in df.iterrows():
    values = []

    for column in columns:
        value = row[column]

        if pd.isna(value):
            value = None

        values.append(value)

    data.append(tuple(values))

print("Inserting records...")

cursor.executemany(insert_query, data)
connection.commit()

print(f"Inserted rows: {cursor.rowcount:,}")

cursor.execute("SELECT COUNT(*) FROM journal_entries")
count = cursor.fetchone()[0]

print(f"Rows in MySQL: {count:,}")

cursor.close()
connection.close()

print("MySQL loading complete.")