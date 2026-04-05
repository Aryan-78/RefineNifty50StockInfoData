import sqlite3
import os
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from helper.helper import csv_root_path, mainDB

def add_all_nifty50_data():
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()

    # Read the CSV
    csv_path = os.path.join(csv_root_path(), 'stock_metadata.csv')
    df = pd.read_csv(csv_path)

    # Insert all symbols
    for _, row in df.iterrows():
        cursor.execute("""
    INSERT INTO nifty50 (company_name, industry, symbol, ISIN) VALUES (?, ?, ?, ?)
    """, (row['Company Name'], row['Industry'], row['Symbol'], row['ISIN Code']))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    add_all_nifty50_data()