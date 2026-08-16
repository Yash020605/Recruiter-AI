import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text
from backend.database.database import engine

def migrate():
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("candidates")]
    
    new_cols = {
        "hiring_success_probability": "FLOAT",
        "predicted_retention_months": "INTEGER"
    }
    
    with engine.begin() as conn:
        for col_name, col_type in new_cols.items():
            if col_name not in columns:
                print(f"Adding column {col_name} to table candidates...")
                conn.execute(text(f"ALTER TABLE candidates ADD COLUMN {col_name} {col_type}"))
                print(f"Column {col_name} added successfully.")
            else:
                print(f"Column {col_name} already exists.")

if __name__ == "__main__":
    migrate()
