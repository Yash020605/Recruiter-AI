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

try:
    cur.execute("ALTER TABLE candidates ADD COLUMN score_breakdown VARCHAR;")
    print("Added score_breakdown")
except psycopg2.errors.DuplicateColumn:
    print("Column score_breakdown already exists")
except Exception as e:
    print(f"Error adding score_breakdown: {e}")

cur.close()
conn.close()
