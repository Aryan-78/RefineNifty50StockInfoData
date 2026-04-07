import subprocess
import os

# Run script to add all nifty 50 companies to the database
subprocess.run(["python", os.path.join("database", "createCsvToData", "createNifty50Table.py")])
subprocess.run(["python", os.path.join("database", "createCsvToData", "addAllnifty50InDatabase.py")])
subprocess.run(["python", os.path.join("database", "createCsvToData", "addIndividualEquityInDatabase.py")])

# Run scripts to modify the database and add additional data
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "addColumnToDatabase.py")])
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "populateResultToDatabase.py")])
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "populateDateToDatabase.py")])
subprocess.run(["python", os.path.join("database", "modifyAdditionalData", "handleMissingData.py")])