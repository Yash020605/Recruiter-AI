import psycopg2
import os
from urllib.parse import urlparse

db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/recruiter_ai")
result = urlparse(db_url)

conn = psycopg2.connect(
    dbname=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
conn.autocommit = True
cur = conn.cursor()
# String columns
string_columns = [
    "current_company",
    "current_ctc",
    "expected_ctc",
    "notice_period",
    "preferred_location",
    "employment_type",
    "immediate_joiner",
    "degree",
    "specialization",
    "college_name",
    "college_tier"
]

# Numeric columns
numeric_columns = {
    "current_ctc_lpa": "FLOAT",
    "expected_ctc_lpa": "FLOAT",
    "notice_period_days": "INTEGER"
}

# Add string columns
for col in string_columns:
    try:
        cur.execute(f"ALTER TABLE candidates ADD COLUMN {col} VARCHAR;")
        print(f"Added {col}")
    except psycopg2.errors.DuplicateColumn:
        print(f"Column {col} already exists")
    except Exception as e:
        print(f"Error adding {col}: {e}")

# Add numeric columns
for col, data_type in numeric_columns.items():
    try:
        cur.execute(
            f"ALTER TABLE candidates ADD COLUMN {col} {data_type};"
        )
        print(f"Added {col}")
    except psycopg2.errors.DuplicateColumn:
        print(f"Column {col} already exists")
    except Exception as e:
        print(f"Error adding {col}: {e}")