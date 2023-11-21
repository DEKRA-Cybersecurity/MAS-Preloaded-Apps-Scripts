import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import mysql.connector  # Import MySQL connector library
# from ..settings import DB_USER_MASA, DB_PASSWORD_MASA
import yaml

import sys
sys.path.append('./')
import utils.formula as formula
from db import database_utils
from sqlalchemy import create_engine
 
# Replace with your actual database connection details
db_config = {
    "host": "localhost",
    "user": 'masa_script',
    "password": 'MASA123',
    "database": "automated_MASA"
}

# Function to extract data from the database for Report table
def extract_data_table1():
    engine = create_engine(f'mysql+mysqlconnector://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')    
    query = "SELECT * FROM Report"
    df = pd.read_sql(query, engine)
    return df

# Function to extract data from the database for Total Fail Counts table
def extract_data_table2():
    engine = create_engine(f'mysql+mysqlconnector://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')    
    query = "SELECT * FROM Total_Fail_Counts"
    df = pd.read_sql(query, engine)
    return df

# Function to extract data from the database for Logging table
def extract_data_table4():
    engine = create_engine(f'mysql+mysqlconnector://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')    
    query = "SELECT * FROM Logging"
    df = pd.read_sql(query, engine)
    return df

# Extract data from the database
df_table1 = extract_data_table1()
df_table2 = extract_data_table2()
df_table4 = extract_data_table4()

# Create a new Excel workbook
workbook = Workbook()
sheet1 = workbook.create_sheet(title='Report')
sheet2 = workbook.create_sheet(title='Total_Fail_Counts')
sheet3 = workbook.create_sheet(title='Formula')
sheet4 = workbook.create_sheet(title='Logging')

# Convert DataFrames to rows and write to the corresponding sheets
for row in dataframe_to_rows(df_table1, index=False, header=True):
    sheet1.append(row)

for row in dataframe_to_rows(df_table2, index=False, header=True):
    sheet2.append(row)

for row in dataframe_to_rows(df_table4, index=False, header=True):
    sheet4.append(row)



# Formula execution and data extraction

database_utils.unify_suid_permissions()
# Obtener la lista de tests del yaml
with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

tests_list = [value.upper() for values in config['tests'].values() for value in values]

value = formula.calculate_formula(0.01, 0.01, tests_list)


sheet3.append(["Formula Value"])
sheet3.append([value])

# Remove the default empty sheet created by openpyxl
if 'Sheet' in workbook.sheetnames:
    default_sheet = workbook['Sheet']
    workbook.remove(default_sheet)

# Save the workbook to a file
workbook.save('./apks/Preload_Analysis.xlsx')