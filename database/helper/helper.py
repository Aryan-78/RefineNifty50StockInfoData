import os

mainDB = "stocks.db"

def csv_root_path():
    return os.path.join(os.path.dirname(__file__), '..\\..', 'archive')   