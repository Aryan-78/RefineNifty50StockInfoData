import sqlite3
import pandas as pd
import sys
from pathlib import Path
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.dataIngestion.addIndividualEquityInDatabase import get_all_symbols
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from helper.enggFeatureInputHelper import (
    get3DayReturn, get10DayReturn, get14DayReturn, getMomentumRatio,
    get3daySlopOf10MovingAverage, get5daySlopOf20MovingAverage, getMovingAverageRatio, getPriceROC, getRSI14, getMACD, getSignalLine, getRange, getVolatility10, getTrueRangeMovingAverage, getTrueRangeMovingAverageRatio, getTrueRangeSpike,
    addingVolumeTrend, getVolumeSpike, getTurnoverSpike, getTradesSpike, getVolumePriceTrend,
    getDeliveryRatio, getDeliverySpike,
    getGap, getClosePosition, getVWAPRatio
)
from helper.helper import mainDB, get_logging

logger = get_logging(Path(__file__).stem)

def get_data_From_old_table(cursor, symbol):
    """Fetch data from the old table."""

    # Get column information
    cursor.execute(f'PRAGMA table_info("{symbol}");')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    # Fetch all data from the table
    select_query = f'SELECT * FROM "{symbol}"'
    try:
        cursor.execute(select_query)
        data = cursor.fetchall()
    except sqlite3.OperationalError as e:
        logger.error(f"Error fetching data from {symbol}: {e}")
        return []
        
    if not data:
        return None
        
    logger.info(f"Processing table: {symbol} with {len(data)-24} rows")
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(data, columns=column_names)
    return df

def superTableWithAllEnggFeatures(cursor, symbol, original_symbol=None):
    """Create a new table with all engineered features."""
    df = get_data_From_old_table(cursor, symbol)
    
    if df is None:
        logger.info(f"No data found for {symbol}. Skipping feature engineering.")
        return
    
    # Calculate engineered features
    newDf = pd.DataFrame()
    newDf['ID'] = df['ID'] 
    newDf['Date'] = df['Date']
    newDf['Day'] = df['Day']
    newDf['Symbol'] = original_symbol or symbol
    newDf['Result'] = df['Result']

    df = df.drop(columns=['Date', 'Day', 'Symbol', 'Series', 'Result'], errors='ignore')

    # Momentum Indicators
    get3DayReturn(newDf,df)
    get10DayReturn(newDf,df)
    get14DayReturn(newDf,df)
    getMomentumRatio(newDf,df)
    
    # Trend Indicators
    get3daySlopOf10MovingAverage(newDf,df)
    get5daySlopOf20MovingAverage(newDf,df)
    getMovingAverageRatio(newDf,df)
    getPriceROC(newDf,df)
    getRSI14(newDf,df)
    getMACD(newDf,df)
    getSignalLine(newDf,df)
    getRange(newDf,df)
    getVolatility10(newDf,df)
    getTrueRangeMovingAverage(newDf,df)
    getTrueRangeMovingAverageRatio(newDf,df)
    getTrueRangeSpike(newDf,df)
    
    # Volume Features
    addingVolumeTrend(newDf,df)
    getVolumeSpike(newDf,df)
    getTurnoverSpike(newDf,df)
    getTradesSpike(newDf,df)
    getVolumePriceTrend(newDf,df)
    
    # Delivery / Smart Money Features
    getDeliveryRatio(newDf,df)
    getDeliverySpike(newDf,df)
    
    # Price Structure Features
    getGap(newDf,df)
    getClosePosition(newDf,df)
    getVWAPRatio(newDf,df)
        
    # Save the new DataFrame to the database
    return  newDf.drop(df.index[:24])

def create_populate_new_table(symbol, cursor, df):
    """Create a new table for the symbol with engineered features."""
    new_table_name = symbol+"_features"
    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS "{new_table_name}" (
            "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
            'Date' TEXT, 
            'Day' TEXT, 
            'Symbol' TEXT, 
            'Result' INTEGER, 
            '3Day_Return' REAL, 
            '10Day_Return' REAL,
            '14Day_Return' REAL, 
            'Momentum_Ratio' REAL, 
            'MA10_slope_3' REAL, 
            'MA20_slope_5' REAL,
            'MA_Ratio' REAL, 
            'Price_ROC' REAL, 
            'RSI14' REAL, 
            'MACD' REAL, 
            'Signal_Line' REAL, 
            'range' REAL,
            'Volatility_10' REAL, 
            'ATR' REAL, 
            'ATR_Ratio' REAL, 
            'ATR_Spike' REAL, 
            'Vol_Trend_5_20' REAL,
            'Volume_Spike' REAL, 
            'Turnover_Spike' REAL, 
            'Trades_Spike' REAL, 
            'Volume_Price_Trend' REAL,
            'Delivery_Ratio' REAL, 
            'Delivery_Spike' REAL, 
            'Gap' REAL, 
            'Close_Position' REAL,
            'VWAP_Ratio' REAL
        )
    '''

    try:
        cursor.execute(create_table_query)
        logger.info(f"New table {new_table_name} created successfully.")
    except sqlite3.OperationalError as e:
        logger.error(f"Error creating table {new_table_name}: {e}")

    df.to_sql(new_table_name, cursor.connection, if_exists="replace", index=False)    

if __name__ == "__main__":
    # Connect to the database
    conn = sqlite3.connect(mainDB)
    cursor = conn.cursor()
    symbols = get_all_symbols()
    for symbol in symbols:
        if symbol == 'M&M':
            table_symbol = 'MM'
        else:
            table_symbol = symbol
        newdf = superTableWithAllEnggFeatures(cursor, symbol=table_symbol, original_symbol=symbol)
        if newdf is not None:
            create_populate_new_table(table_symbol, cursor, newdf)
    conn.close()
