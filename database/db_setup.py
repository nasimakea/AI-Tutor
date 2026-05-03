import pandas as pd
import os
from database.db_connection import get_db_connection
from config.config import Config

def initialize_database():
    """Creates tables from CSV files in the datasets folder."""
    conn = get_db_connection()
    
    # Define which tables to create from which CSVs
    datasets = {
        "employees": os.path.join(Config.DATASETS_PATH, "employees.csv"),
        "sales": os.path.join(Config.DATASETS_PATH, "sales.csv")
    }
    
    for table_name, csv_path in datasets.items():
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                # to_sql handles the table creation and data insertion
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"✅ Successfully created table: {table_name}")
            except Exception as e:
                print(f"❌ Error loading {csv_path}: {e}")
        else:
            print(f"⚠️ Warning: File not found at {csv_path}")
            
    conn.close()
    print("🚀 Database initialization complete.")

if __name__ == "__main__":
    initialize_database()