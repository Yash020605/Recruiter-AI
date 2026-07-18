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
    cur.execute("ALTER TYPE userrole RENAME TO userrole_old;")
    cur.execute("CREATE TYPE userrole AS ENUM ('admin', 'recruiter', 'hiring_manager');")
    cur.execute("TRUNCATE TABLE users;")
    cur.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT;")
    cur.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::text::userrole;")
    cur.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'recruiter'::userrole;")
    cur.execute("DROP TYPE userrole_old;")
    print("Roles migrated successfully")
except Exception as e:
    print(f"Error migrating roles (it might have already run): {e}")

cur.close()
conn.close()
