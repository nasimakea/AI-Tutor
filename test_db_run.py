from src.components.query_runner import QueryRunner
from database.db_setup import initialize_database
import os

# 1. Ensure DB is setup
if not os.path.exists("database/sql_tutor.db"):
    print("Initializing Database...")
    initialize_database()

# 2. Try a real query
runner = QueryRunner()
print("--- Testing Valid Query ---")
res = runner.run_query("SELECT * FROM employees LIMIT 2")
if res["success"]:
    print("Data found:")
    print(res["result"])
else:
    print(f"Error: {res['error']}")

print("\n--- Testing Invalid SQL Syntax ---")
res_bad = runner.run_query("SELECT * FROM nonexistent_table")
print(f"Caught Error: {res_bad['error']}")