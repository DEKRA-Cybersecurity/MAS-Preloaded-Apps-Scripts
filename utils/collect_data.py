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
from utils.auxiliar_functions import use_semgrep, dekra_script_version
 
# Replace with your actual database connection details
db_config = {
    "host": "localhost",
    "user": 'masa_script',
    "password": 'MASA123',
    "database": "automated_MASA"
}

TABLE_REPORT = 'Report'
TABLE_FAIL_COUNTS = 'Total_Fail_Counts'
TABLE_LOGGING = 'Logging'
TABLE_SEMGREP = 'SEMGREP_FINDINGS'

def extract_data(table_name):
    engine = create_engine(f'mysql+mysqlconnector://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')    
    query = "SELECT * FROM " + table_name
    df = pd.read_sql(query, engine)
    return df


def collect_data_dekra(dekra):
    # Extract data from the database
    report_table = extract_data(TABLE_REPORT)
    fail_counts_table = extract_data(TABLE_FAIL_COUNTS)
    logging_table = extract_data(TABLE_LOGGING)

    # Create a new Excel workbook
    workbook = Workbook()
    report_sheet = workbook.create_sheet(title='Report')
    fail_counts_sheet = workbook.create_sheet(title='Total_Fail_Counts')
    formula_sheet = workbook.create_sheet(title='Formula')
    logging_sheet = workbook.create_sheet(title='Logging')

    # Convert DataFrames to rows and write to the corresponding sheets
    for row in dataframe_to_rows(report_table, index=False, header=True):
        report_sheet.append(row)

    for row in dataframe_to_rows(fail_counts_table, index=False, header=True):
        fail_counts_sheet.append(row)

    for row in dataframe_to_rows(logging_table, index=False, header=True):
        logging_sheet.append(row)

    # Formula execution and data extraction
    database_utils.unify_suid_permissions()

    # Obtain test list
    with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

    tests_list = [value.upper() for values in config['tests'].values() for value in values]

    value = formula.calculate_formula(0.01, 0.01, tests_list)

    formula_sheet.append(["Formula Value"])
    formula_sheet.append([value])

    # Remove the default empty sheet created by openpyxl
    if 'Sheet' in workbook.sheetnames:
        default_sheet = workbook['Sheet']
        workbook.remove(default_sheet)

    version = dekra_script_version()

    # Save the workbook to a file
    workbook.save('./apks/Preload_Analysis_' + version + '.xlsx')


def collect_data_semgrep(dekra):
    report_table = extract_data(TABLE_REPORT)
    finding_table = extract_data(TABLE_SEMGREP)

    # Create a new Excel workbook
    workbook = Workbook()
    report_sheet = workbook.create_sheet(title='Report')
    report_findings = workbook.create_sheet(title='Findings')

    # Convert DataFrames to rows and write to the corresponding sheets
    for row in dataframe_to_rows(report_table, index=False, header=True):
        report_sheet.append(row)

    # Convert DataFrames to rows and write to the corresponding sheets
    for row in dataframe_to_rows(finding_table, index=False, header=True):
        report_findings.append(row)
    
    # Remove the default empty sheet created by openpyxl
    if 'Sheet' in workbook.sheetnames:
        default_sheet = workbook['Sheet']
        workbook.remove(default_sheet)

    version = dekra_script_version()

    # Save the workbook to a file
    workbook.save('./apks/Preload_Analysis_' + version + '.xlsx')

if __name__ == "__main__":
    # Averiguar si se ha usado semgrep o no
    dekra = not use_semgrep()

    if dekra:
        collect_data_dekra(dekra)
    else:
        collect_data_semgrep(dekra)
