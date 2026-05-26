from pathlib import Path
import sqlite3
import pandas as pd
import sys
import os

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.database.dataIngestion.addIndividualEquityInDatabase import get_all_symbols
from helper.helper import mainDB, get_logging

logger = get_logging(Path(__file__).stem)
# This function creates a final dataset by combining the feature tables of all symbols. It aligns the features with the corresponding results to ensure that the model can learn effectively.
"""
    FeatureTable Structure:

    Feature1  Feature2  Feature3  Result
    0.5       1.2       0.3       1
    0.6       1.0       0.4       0
    0.4       1.1       0.2       1

    Dataset Structure:

    Feature1  Feature2  Feature3  Result
    0.5       1.2       0.3       0
    0.6       1.0       0.4       1

"""

def finalFeatureEngineerTable():
    symbols = get_all_symbols()
    for symbol in symbols:
        if symbol == 'M&M':
            symbol = 'MM'
        featureTable = symbol + "_features"
        try:    
            with sqlite3.connect(mainDB) as conn:
                cursor = conn.cursor()
                df = pd.read_sql_query(f"SELECT * FROM '{featureTable}' WHERE Result IS NOT NULL;", conn)
                superdf = pd.DataFrame()
                # Check if the feature table already exists

                superdf = df.iloc[:-1, df.columns != 'Result']
                superdf['Result'] = df['Result'].iloc[1:].reset_index(drop=True)
                superdf.to_sql("dataSetTable", conn, if_exists='append', index=False)

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    logger.info("Final dataset creation completed.")

if __name__ == "__main__":
    sqlite3.connect(mainDB)
    finalFeatureEngineerTable()