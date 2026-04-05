import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from createCsvToData.addIndividualEquityInDatabase import get_all_symbols
from helper.helper import mainDB

# This script is responsible for populating the 'Result' column in the database for each stock symbol.
def populate_result_to_database(symbol):
    # Check for all the 10th records in the table for the given symbol and determine if the stock price went up or down compared to the 1st day.
    
    #Connect to the database
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()

    # Fetch all records for the given symbol ordered by date
    cursor.execute(f"""
        SELECT * FROM "{symbol}"
        ORDER BY "Date" ASC
    """)
    records = cursor.fetchall()
    
    # If there are less than 10 records, we cannot determine the result, so we will skip that symbol.
    if len(records) < 10:
        print(f"Not enough records for {symbol} to determine the result. Skipping.")
        conn.close()
        return

    # In the Progressive Step of 10 days, if the stock price increased by 7% or more, we will consider it as a positive result (1), otherwise negative (0).
    a = len(records)
    initial_stock_order = 0 # Starting from the first record
    final_stock_order = initial_stock_order + 9 # 10th record (index 9)
    while final_stock_order < a:
        first_day_close = records[initial_stock_order][9]  # Assuming 'Close' is the 10th column (index 9)
        tenth_day_close = records[final_stock_order][9]  # 10th record
        
        # if there is a 7% or more increase in the stock price, then we will consider it as a positive result (1), otherwise negative (0).
        price_change_percentage = ((tenth_day_close - first_day_close) / first_day_close) * 100        
        cursor.execute(f"""
            UPDATE "{symbol}"
            SET "Result" = ?
            WHERE "Date" = ?
        """, (1 if price_change_percentage >= 7 else 0, records[final_stock_order][0]))  # Assuming 'Date' is the first column (index 0)    
        initial_stock_order = final_stock_order + 1
        final_stock_order += 9
    conn.commit()
    print(f"Result column populated for {symbol}.")
    conn.close()

if __name__ == "__main__":
    symbols = get_all_symbols()
    for symbol in symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        populate_result_to_database(symbol)