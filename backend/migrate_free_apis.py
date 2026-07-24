import sqlite3

def run_migration():
    conn = sqlite3.connect('recruiter.db')
    cursor = conn.cursor()
    
    # Adding new columns
    columns_to_add = [
        ("google_meet_url", "VARCHAR"),
        ("github_score", "FLOAT"),
        ("google_sheets_sync_status", "VARCHAR")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE candidates ADD COLUMN {col_name} {col_type};")
            print(f"Added column {col_name} to candidates table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    run_migration()
