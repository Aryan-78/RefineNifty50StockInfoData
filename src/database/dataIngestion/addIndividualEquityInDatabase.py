from pathlib import Path
import sqlite3
import os
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from helper.helper import csv_root_path, get_logging, mainDB

logger = get_logging(Path(__file__).stem)

def get_all_symbols():
    """Retrieve all stock symbols from the database."""
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT symbol FROM nifty50")
    symbols = cursor.fetchall()
    
    conn.close()

    logger.info(f"Retrieved {len(symbols)} symbols from the nifty50 table.")

    return [symbol[0] for symbol in symbols]

def fetch_data_from_csv(csv_path):
    """Fetch stock data from a CSV file."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Successfully read data from {csv_path}")
    except Exception as e:
        logger.error(f"Error reading {csv_path}: {e}")
        df = pd.DataFrame()
    df = df.where(pd.notna(df), None)
    return df

def get_all_stock_data():
    """Get all stock data from CSV files, create tables, and insert data into stocks.db."""
    symbols = get_all_symbols()
    conn = sqlite3.connect(mainDB)

    logger.info("Starting to fetch all stock data...")
    
    for symbol in symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        csv_path = os.path.join(csv_root_path(), f'{symbol}.csv')
        if os.path.exists(csv_path):
            df = fetch_data_from_csv(csv_path)
            if df.empty:
                logger.warning(f"No data found in CSV for {symbol}. Skipping.")
                continue
            # Create table and insert data
            df.to_sql(symbol, conn, if_exists='replace', index=False)
            logger.info(f"Data for {symbol} inserted into table {symbol}.")
        else:
            logger.warning(f"CSV file for {symbol} not found.")
    
    conn.close()

if __name__ == "__main__":
    logger.info("Starting to get all stock data and insert into database...")
    get_all_stock_data()
    