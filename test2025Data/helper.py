nifty50_symbols_2025 = ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO",
    "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "ITC", "INDUSINDBK", "INFY", "JIOFIN", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NTPC",
    "NESTLEIND", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SHRIRAMFIN", "SBIN", "SUNPHARMA",
    "TATACONSUM", "TCS", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", "TRENT", "ULTRACEMCO",
    "WIPRO"
]

database = "new.db"
primaryTableName = "AllData"

def createTableQuery(tableName):

    query = f"""
            CREATE TABLE {tableName} (
                "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
                SYMBOL TEXT,
                SERIES TEXT,
                DATE1 DATE,

                PREV_CLOSE REAL,
                OPEN_PRICE REAL,
                HIGH_PRICE REAL,
                LOW_PRICE REAL,
                LAST_PRICE REAL,
                CLOSE_PRICE REAL,
                AVG_PRICE REAL,

                TTL_TRD_QNTY REAL,
                TURNOVER_LACS REAL,
                NO_OF_TRADES REAL,
                DELIV_QTY REAL,
                DELIV_PER REAL
            );
            """
    return query