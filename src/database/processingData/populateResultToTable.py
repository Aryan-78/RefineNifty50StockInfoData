import sqlite3
import sys
import os

from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dataIngestion.addIndividualEquityInDatabase import get_all_symbols
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from helper.helper import get_logging, mainDB

logger = get_logging(Path(__file__).stem)

def get_table_schema(table_name):
    """Get column information for a specified table."""
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns_info = cursor.fetchall()
    # print(columns_info)
    return columns_info


# This script is responsible for populating the 'Result' column in the database for each stock symbol.
def populate_result_to_database(symbol):
    # Check for all the 10th records in the table for the given symbol and determine if the stock price went up or down compared to the 1st day.
    
    #Connect to the database
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()

    column_info = get_table_schema(symbol)

    closeIndex = next( i for i, col in enumerate(column_info) if col[1] == "Close" )
    dateIndex = next(i for i, col in enumerate(column_info) if col[1] == "Date")

    # Fetch all records for the given symbol ordered by date
    cursor.execute(f"""
        SELECT * FROM "{symbol}"
        ORDER BY "ID" ASC
    """)
    records = cursor.fetchall()
    
    # If there are less than 10 records, we cannot determine the result, so we will skip that symbol.
    if len(records) < 10:
        logger.info(f"Not enough records for {symbol} to determine the result. Skipping.")
        conn.close()
        return

    # In the Progressive Step of 10 days, if the stock price increased by 7% or more, we will consider it as a positive result (1), otherwise negative (0).
    a = len(records)
    initial_stock_order = 0 # Starting from the first record
    final_stock_order = initial_stock_order + 9 # 10th record (index 9)
    while final_stock_order < a:
        first_day_close = records[initial_stock_order][closeIndex]
        tenth_day_close = records[final_stock_order][closeIndex]  # 10th record
        
        # if there is a 7% or more increase in the stock price, then we will consider it as a positive result (1), otherwise negative (0).
        price_change_percentage = ((tenth_day_close - first_day_close) / first_day_close) * 100        
        cursor.execute(f"""
            UPDATE "{symbol}"
            SET "Result" = ?
            WHERE "Date" = ?
        """, (1 if price_change_percentage >= 7 else 0, records[final_stock_order][dateIndex]))    
        initial_stock_order = final_stock_order + 1
        final_stock_order += 9
    conn.commit()
    logger.info(f"Result column populated for {symbol}.")
    conn.close()

if __name__ == "__main__":
    logger.info("Starting to populate 'Result' column in the database...")
    symbols = get_all_symbols()
    for symbol in symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        populate_result_to_database(symbol)