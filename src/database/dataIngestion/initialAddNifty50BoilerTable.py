from pathlib import Path
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((__file__))))))
from helper.helper import get_logging, mainDB

logger = get_logging(Path(__file__).stem)


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
    logger.info("Creating nifty50 table in the database...")
    create_nifty50_table(mainDB)