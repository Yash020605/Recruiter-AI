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

columns = [
    "current_company",
    "current_ctc",
    "expected_ctc",
    "notice_period",
    "preferred_location",
    "employment_type",
    "immediate_joiner"
]

for col in columns:
    try:
        cur.execute(f"ALTER TABLE candidates ADD COLUMN {col} VARCHAR;")
        print(f"Added {col}")
    except psycopg2.errors.DuplicateColumn:
        print(f"Column {col} already exists")
    except Exception as e:
        print(f"Error adding {col}: {e}")

cur.close()
conn.close()
