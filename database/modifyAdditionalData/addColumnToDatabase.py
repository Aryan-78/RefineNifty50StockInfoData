from pathlib import Path
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from createCsvToData.addIndividualEquityInDatabase import get_all_symbols
from helper.helper import get_logging, mainDB

logger = get_logging(Path(__file__).stem)

def create_new_table_with_symbol(symbol):
    """Create a new table with the same schema as the original table and add a 'day' column."""
    new_table_name = f"{symbol}_new"
    
    # Check if the new table already exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{new_table_name}'")
    if cursor.fetchone() is not None:
        logger.info(f"Table {new_table_name} already exists. Skipping creation.")
        return
    
    create_table_query = f"""
        CREATE TABLE "{new_table_name}" (
            "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Date" TEXT,
            "Day" TEXT,
            "Symbol" TEXT,
            "Series" TEXT,
            "Prev Close" REAL,
            "Open" REAL,
            "High" REAL,
            "Low" REAL,
            "Last" REAL,
            "Close" REAL,
            "VWAP" REAL,
            "Volume" INTEGER,
            "Turnover" REAL,
            "Trades" REAL,
            "Deliverable Volume" REAL,
            "%Deliverble" REAL,  
            "Result" INTEGER
        );
    """
    try:
        cursor.execute(create_table_query)
        logger.info(f"New table {new_table_name} created successfully.")
    except sqlite3.OperationalError as e:
        logger.error(f"Error creating table {new_table_name}: {e}")

def populate_new_table_with_data(symbol):
    """Populate the new table with data from the original table."""
    new_table_name = f"{symbol}_new"

    # if the new table is already populated then skip the population
    cursor.execute(f"SELECT COUNT(*) FROM '{new_table_name}'")
    if cursor.fetchone()[0] > 0:
        logger.info(f"Table {new_table_name} is already populated. Skipping population.")
        return

    insert_query = f"""
        INSERT INTO "{new_table_name}" (Date, Day, Symbol, Series, "Prev Close", Open, High, Low, Last, Close, VWAP, Volume, Turnover, Trades, "Deliverable Volume", "%Deliverble", Result)
        SELECT Date, NULL AS Day, Symbol, Series, "Prev Close", Open, High, Low, Last, Close, VWAP, Volume, Turnover, Trades, "Deliverable Volume", "%Deliverble", NULL AS Result
        FROM "{symbol}"
    """
    try:
        cursor.execute(insert_query)
        conn.commit()
        logger.info(f"Data from {symbol} inserted into {new_table_name} successfully.")
    except sqlite3.OperationalError as e:
        logger.error(f"Error inserting data into {new_table_name}: {e}")

def delete_old_table(symbol):
    """Delete the old table after populating the new table."""

    # Check if the old table exists before attempting to delete it
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{symbol}'")
    if cursor.fetchone() is None:
        logger.info(f"Table {symbol} does not exist. Skipping deletion.")
        return

    delete_query = f'DROP TABLE IF EXISTS "{symbol}"'
    try:
        cursor.execute(delete_query)
        logger.info(f"Old table {symbol} deleted successfully.")
    except sqlite3.OperationalError as e:
        logger.error(f"Error deleting table {symbol}: {e}")

def rename_new_table(symbol):
    """Rename the new table to the original table name."""
    
    new_table_name = f"{symbol}_new"
    
    # Check if the new table exists before attempting to rename it
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{new_table_name}'")
    if cursor.fetchone() is None:
        logger.info(f"Table {new_table_name} does not exist. Skipping renaming.")
        return
    
    rename_query = f'ALTER TABLE "{new_table_name}" RENAME TO "{symbol}"'
    try:
        cursor.execute(rename_query)
        logger.info(f"Table {new_table_name} renamed to {symbol} successfully.")
    except sqlite3.OperationalError as e:
        logger.error(f"Error renaming table {new_table_name}: {e}")

if __name__ == "__main__":
    # Get all symbols from the database
    symbols = get_all_symbols()

    # Create a new table for all symbols adding suffix '_new' to the table name and for MM create a new table with name MM_new and day column to it after date column using its schema
    for symbol in symbols:
        logger.info("Altering database to add new equity...")
        conn = sqlite3.connect(mainDB)
        cursor = conn.cursor()

        if symbol == "M&M":
            symbol = "MM"
        create_new_table_with_symbol(symbol)
        populate_new_table_with_data(symbol)
        delete_old_table(symbol)
        rename_new_table(symbol)

        conn.close()