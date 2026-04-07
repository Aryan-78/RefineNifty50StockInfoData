import sqlite3
import sys
import os

from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from createCsvToData.addIndividualEquityInDatabase import get_all_symbols
from helper.helper import get_logging, mainDB

logger = get_logging(Path(__file__).stem)

def add_day_data_to_table(symbol):
    """Add 'Day' column to a stock table and populate it with the day of the week."""
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()
        
    # Check if the new table already exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{symbol}'")
    if cursor.fetchone() is None:
        logger.info(f"Table {symbol} does not exist. Skipping.")
        conn.close()
        return

    # Update the 'Day' column with the day of the week based on the 'Date' column
    update_query = f"""
        UPDATE "{symbol}"
        SET "Day" = 
            CASE 
                WHEN strftime('%w', "Date") = '0' THEN 'Sunday'
                WHEN strftime('%w', "Date") = '1' THEN 'Monday'
                WHEN strftime('%w', "Date") = '2' THEN 'Tuesday'
                WHEN strftime('%w', "Date") = '3' THEN 'Wednesday'
                WHEN strftime('%w', "Date") = '4' THEN 'Thursday'
                WHEN strftime('%w', "Date") = '5' THEN 'Friday'
                WHEN strftime('%w', "Date") = '6' THEN 'Saturday'
            END
        """
    try:
        cursor.execute(update_query)
        logger.info(f"'Day' column updated for table {symbol}.")
    except sqlite3.OperationalError as e:
        logger.error(f"Error updating table {symbol}: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    logger.info("Starting to add 'Day' data to tables...")
    symbols = get_all_symbols()
    for symbol in symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        add_day_data_to_table(symbol)