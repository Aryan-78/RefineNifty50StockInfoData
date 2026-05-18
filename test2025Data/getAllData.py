from nselib import capital_market as cm
import nselib
from datetime import datetime, timedelta
import sqlite3
from helper import database,nifty50_symbols_2025, primaryTableName, createTableQuery

dates_2025 = []
lalaDates = ['26-05-2025', '27-05-2025', '28-05-2025', '29-05-2025', '30-05-2025', '02-06-2025', '03-06-2025', '04-06-2025', '05-06-2025', '06-06-2025', '09-06-2025', '10-06-2025', '11-06-2025']
missingdate = []

def getAllDateTime():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)

    current_date = start_date
    currCounter = 3
    while current_date <= end_date:
        if currCounter <= 5:
            dates_2025.append(current_date.strftime("%d-%m-%Y"))
        current_date += timedelta(days=1)
        if currCounter == 7:
            currCounter = 1
        else: 
            currCounter += 1
            

def getAllBhavs(cursor):
    count = 0
    for date in dates_2025:
        try:
            data = cm.bhav_copy_with_delivery(date)
            df = data[data['SYMBOL'].isin(nifty50_symbols_2025)]
            count += len(df)
            df.to_sql("AllData", cursor.connection, if_exists="append", index=False)
        except Exception as e:
            missingdate.append(date)
            print(f"Error processing {date}: {e}")

    print(f' Total col {count}')
    print(missingdate)

def createDatabase(cursor):

    query = createTableQuery(primaryTableName)

    try:
        cursor.execute(query)
    except sqlite3.OperationalError as e:
        print(f'ERROR : {e}')

if __name__ == "__main__":

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    createDatabase(cursor)
    getAllDateTime()
    getAllBhavs(cursor)
    conn.close()
