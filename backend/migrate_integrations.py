import sqlite3

db_path = "recruiter.db"

columns = {
    "linkedin_profile_url": "VARCHAR",
    "hirevue_interview_url": "VARCHAR",
    "codility_score": "FLOAT",
    "calendly_interview_time": "VARCHAR",
    "tableau_export_status": "VARCHAR"
}

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for col, data_type in columns.items():
        try:
            cur.execute(f"ALTER TABLE candidates ADD COLUMN {col} {data_type};")
            print(f"Added {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col} already exists")
            else:
                print(f"Error adding {col}: {e}")
    conn.commit()
except Exception as e:
    print(f"Connection error: {e}")
finally:
    if conn:
        conn.close()
