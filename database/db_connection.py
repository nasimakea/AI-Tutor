import sqlite3
from config.config import Config

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
    # This allows us to access columns by name like row['name']
    conn.row_factory = sqlite3.Row 
    return conn