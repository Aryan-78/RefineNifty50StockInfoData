import subprocess
import os
from database.helper.helper import mainDB, LOG_FILE

# preCleanUp bring the folder into its initial state
def preCleanUp():
    if os.path.exists(mainDB):
        os.remove(mainDB)
    
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

preCleanUp()

# Run script to add all nifty 50 companies to the database
subprocess.run(["python", os.path.join("database", "createCsvToData", "createNifty50Table.py")])
subprocess.run(["python", os.path.join("database", "createCsvToData", "addAllnifty50InDatabase.py")])
subprocess.run(["python", os.path.join("database", "createCsvToData", "addIndividualEquityInDatabase.py")])

# Run scripts to modify the database and add additional data
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "addColumnToDatabase.py")])
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "populateResultToDatabase.py")])
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "populateDateToDatabase.py")])
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "handleMissingData.py")])