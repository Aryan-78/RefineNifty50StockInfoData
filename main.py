import subprocess
import os
from src.helper.helper import mainDB, LOG_FILE

# preCleanUp bring the folder into its initial state
def preCleanUp():
    if os.path.exists(mainDB):
        os.remove(mainDB)
    
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

preCleanUp()

# Run script to add all nifty 50 companies to the database
subprocess.run(["python", os.path.join("src", "database", "dataIngestion", "initialAddNifty50BoilerTable.py")])
subprocess.run(["python", os.path.join("src", "database", "dataIngestion", "populateNifty50Table.py")])
subprocess.run(["python", os.path.join("src", "database", "dataIngestion", "addIndividualEquityInDatabase.py")])

# Run scripts to modify the database and add additional data
subprocess.run(["python", os.path.join("src", "database", "processingData", "addDayAndResultColumn.py")])
subprocess.run(["python", os.path.join("src", "database", "processingData", "populateResultToTable.py")])
subprocess.run(["python", os.path.join("src", "database", "processingData", "populateDateToTable.py")])
subprocess.run(["python", os.path.join("src", "database", "processingData", "handleMissingData.py")])

# Run scripts to get Engineering data to the database
subprocess.run(["python", os.path.join("src", "addFeature", "addFeatureTable.py")])
