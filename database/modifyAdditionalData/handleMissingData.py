from pathlib import Path
from sklearn.impute import KNNImputer
import sqlite3  
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from helper.helper import get_logging
from createCsvToData.addIndividualEquityInDatabase import get_all_symbols

logger = get_logging(Path(__file__).stem)       

# Function to add missing data to tables using KNN imputation
def add_missing_data_to_tables():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        if table_name == "nifty50":
            continue

        # Get column information
        cursor.execute(f'PRAGMA table_info("{table_name}");')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Fetch all data from the table
        cursor.execute(f'SELECT * FROM "{table_name}";')
        data = cursor.fetchall()
        
        if not data:
            continue
            
        logger.info(f"Processing table: {table_name} with {len(data)} rows")
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(data, columns=column_names)
        
        # Check which columns have missing values
        columns_with_missing = []
        for col in column_names:
            if col in ['Date', 'Day', 'Symbol', 'Series', 'Result']:
                continue  # Skip non-numeric columns
            null_count = df[col].isnull().sum()
            if null_count > 0:
                columns_with_missing.append((col, null_count))
        
        if not columns_with_missing:
            logger.info(f"No missing values found in {table_name}")
            continue
        
        logger.info(f"Found missing values in: {columns_with_missing}")
        
        # Prepare data for KNN imputation
        # Convert to numeric types where possible
        df_numeric = df.copy()
        for col in df_numeric.columns:
            if col in ['Date', 'Day', 'Symbol', 'Series', 'Result']:
                # Keep categorical/string columns as is for now
                continue
            try:
                df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
            except:
                continue
        
        # Select only numeric columns for imputation
        numeric_cols = df_numeric.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            logger.info(f"No numeric columns found in {table_name}")
            continue
        
        # Apply KNN imputation
        imputer = KNNImputer(n_neighbors=5)
        imputed_array = imputer.fit_transform(df_numeric[numeric_cols])
        
        # Update the DataFrame with imputed values
        df_imputed = pd.DataFrame(imputed_array, columns=numeric_cols)
        
        # Update the database with imputed values for columns that had missing data
        total_imputed = 0
        for col, null_count in columns_with_missing:
            if col in df_imputed.columns:
                originally_missing = df[col].isnull()
                imputed_values = df_imputed.loc[originally_missing, col]
                
                for idx, new_value in zip(originally_missing[originally_missing].index, imputed_values):
                    if pd.notna(new_value):
                        cursor.execute(f'UPDATE "{table_name}" SET "{col}" = ? WHERE rowid = ?;', 
                                        (float(new_value), idx + 1))
                        total_imputed += 1
        
        logger.info(f"Successfully imputed {total_imputed} missing values across {len(columns_with_missing)} columns")
    
    conn.commit()
    conn.close()

def ignore_missing_data():
    SqliteConnection = sqlite3.connect('stocks.db')
    cursor = SqliteConnection.cursor()
    Symbols = get_all_symbols()

    for symbol in Symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        cursor.execute(f'SELECT * FROM "{symbol}";')
        data = cursor.fetchall()
        if not data:
            logger.warning(f"No data found for {symbol}.")
            continue
        
        df = pd.DataFrame(data, columns=[col[0] for col in cursor.description])
        df.dropna(inplace=True)

        df.to_sql(symbol, SqliteConnection, if_exists='replace', index=False)
        logger.info(f"Missing data for {symbol} has been ignored and the table has been updated.")


if __name__ == "__main__":
    logger.info("Script to handle missing data in the database has started.")
    a = input("This script will add missing data to the tables using KNN imputation. Enter Y to continue or N to ignore those ")
    if a.upper() == "Y":
        logger.info("User chose to add missing data using KNN imputation. Starting the imputation process...")
        add_missing_data_to_tables()
    if a.upper() == "N":
        logger.info("User chose to ignore missing data. Proceeding to remove rows with missing values.")
        ignore_missing_data()
