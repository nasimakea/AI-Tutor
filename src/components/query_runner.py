import sqlite3
import pandas as pd
from database.db_connection import get_db_connection


class QueryRunner:

    @staticmethod
    def run_query(query: str):
        """
        Executes a SQL query against the SQLite database.
        Returns a dictionary with success status, the data (if any), and error messages.
        """
        conn = get_db_connection()
        try:
            # Allow only SELECT queries
            if not query.strip().lower().startswith("select"):
                return {
                    "success": False,
                    "result": None,
                    "error": "For safety, only SELECT queries are allowed in this tutor."
                }

            df = pd.read_sql_query(query, conn)

            return {
                "success": True,
                "result": df,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }

        finally:
            conn.close()

    def get_schema_dict(self):
        """
        Fetches table names, their column lists, and a sample of data (first 3 rows).
        Returns: { "table_name": {"columns": [...], "sample": [...] } }
        """
        conn = get_db_connection()

        try:
            cursor = conn.cursor()

            # Get all user-defined tables
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%';
            """)
            tables = [row[0] for row in cursor.fetchall()]

            schema = {}

            for table in tables:
                # Fetch columns
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]

                # Fetch sample rows
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                    sample_rows = cursor.fetchall()
                except Exception:
                    sample_rows = []

                schema[table] = {
                    "columns": columns,
                    "sample": sample_rows
                }

            return schema

        except Exception:
            return {}

        finally:
            conn.close()

    def validate_locally(self, user_sql: str, expected_sql: str):
        """
        Validates user SQL against expected SQL by comparing actual result sets.
        This avoids calling the AI API for every single attempt.
        """
        conn = get_db_connection()
        try:
            # Execute both queries
            user_df = pd.read_sql_query(user_sql, conn)
            expected_df = pd.read_sql_query(expected_sql, conn)

            # Compare Dataframes (ignores row order to be more flexible for learners)
            # Use sort_values if you want to be strict, but .equals() is good for exact matches
            is_correct = user_df.equals(expected_df)

            return {
                "is_correct": is_correct,
                "result": user_df,
                "error": None
            }
        except Exception as e:
            return {
                "is_correct": False,
                "result": None,
                "error": str(e)
            }
        finally:
            conn.close()