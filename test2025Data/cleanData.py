from helper import database, nifty50_symbols_2025, primaryTableName, createTableQuery
import sqlite3
import pandas as pd

def getData():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    for symbol in nifty50_symbols_2025:
        print(symbol)

        # Get column information
        cursor.execute(f'PRAGMA table_info("{primaryTableName}");')
        columns = cursor.fetchall()
        print(columns)
        column_names = [col[1] for col in columns]
        
        query = createTableQuery(symbol)
        try :
            cursor.execute(query)        
        except:
            print(f"already exist table : {symbol}")
        query = f" SELECT * FROM {primaryTableName} WHERE SYMBOL == '{symbol}' "
        try:
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as e :
            print(f"some error occur while fetching the data : {e} ")
        df = pd.DataFrame(data, columns=column_names)
        df.to_sql(symbol, cursor.connection, if_exists="replace", index=False)


if __name__ == "__main__":
    getData()