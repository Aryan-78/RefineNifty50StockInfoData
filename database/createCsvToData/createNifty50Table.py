import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from helper.helper import mainDB

def createDataBase(DB_NAME):
    """Create a new database and connect to it."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_nifty50_table(DB_NAME):
    """Create the nifty50 table if it doesn't exist."""
    conn = createDataBase(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nifty50 (
        company_name TEXT,
        industry TEXT,
        symbol TEXT,
        ISIN TEXT primary key
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_nifty50_table(mainDB)