from asyncio.log import logger
import os
import logging

LOG_FILE = "allLogs.log"
mainDB = "stocks.db"


def csv_root_path():
    return os.path.join(os.path.dirname(__file__), '..\\..', 'archive')   

def get_logging(name):
    log_filename = LOG_FILE
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger