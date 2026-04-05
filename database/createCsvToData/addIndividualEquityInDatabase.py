import sqlite3
import os
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from helper.helper import csv_root_path, mainDB


def get_all_symbols():
    """Retrieve all stock symbols from the database."""
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT symbol FROM nifty50")
    symbols = cursor.fetchall()
    
    conn.close()
    
    return [symbol[0] for symbol in symbols]

def fetch_data_from_csv(csv_path):
    """Fetch stock data from a CSV file."""
    df = pd.read_csv(csv_path)
    df = df.where(pd.notna(df), None)
    return df

def get_all_stock_data():
    """Get all stock data from CSV files, create tables, and insert data into stocks.db."""
    symbols = get_all_symbols()
    conn = sqlite3.connect(mainDB)
    archive_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archive')
    
    for symbol in symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        csv_path = os.path.join(csv_root_path(), f'{symbol}.csv')
        if os.path.exists(csv_path):
            df = fetch_data_from_csv(csv_path)
            # Create table and insert data
            df.to_sql(symbol, conn, if_exists='replace', index=False)
            print(f"Data for {symbol} inserted into table {symbol}.")
        else:
            print(f"Warning: CSV file for {symbol} not found.")
    
    conn.close()

if __name__ == "__main__":
    get_all_stock_data()
    