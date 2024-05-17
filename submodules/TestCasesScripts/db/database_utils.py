import mysql.connector
from settings import DB_USER_MASA, DB_PASSWORD_MASA, DB_HOST_MASA
import yaml

def first_execution(database='automated_MASA'):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()

    # cursor.execute('CREATE DATABASE ' + database)

    cursor.execute('USE ' + database)

    cursor.execute('''
        CREATE TABLE Executions (
            ID VARCHAR(255) PRIMARY KEY,
            TIMESTAMP VARCHAR(255),
            RISK_SCORE DOUBLE
        )
    ''')

    cursor.execute('''
        CREATE TABLE TestSSL_URLS (
            URL VARCHAR(255) PRIMARY KEY,
            RESULT VARCHAR(255)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Findings (
            HASH VARCHAR(255),
            ID_EXECUTION VARCHAR(255),
            APP_NAME VARCHAR(255),
            CATEGORY VARCHAR(255),
            CHECK_ID VARCHAR(255),
            PATH VARCHAR(255),
            LINE VARCHAR(255)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Report (
            HASH VARCHAR(255),
            ID_EXECUTION VARCHAR(255),
            APP_NAME VARCHAR(255),
            VERSION_NAME VARCHAR(255),
            SEMGREP BOOLEAN,
            SCRIPT_VERSION VARCHAR(255),
            CODE_1 VARCHAR(255),
            CODE_2 VARCHAR(255),
            CRYPTO_1 VARCHAR(255),
            CRYPTO_3 VARCHAR(255),
            NETWORK_1 VARCHAR(255),
            NETWORK_2 VARCHAR(255),
            NETWORK_3 VARCHAR(255),
            PLATFORM_2 VARCHAR(255),
            PLATFORM_3 VARCHAR(255),
            STORAGE_2 VARCHAR(255),
            PRIMARY KEY (HASH, ID_EXECUTION)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Total_Fail_Counts (
            HASH VARCHAR(255),
            ID_EXECUTION VARCHAR(255),
            CODE_1 INT(10),
            CODE_2 INT(10),
            CRYPTO_1 INT(10),
            CRYPTO_3 INT(10),
            NETWORK_1 INT(10),
            NETWORK_2 INT(10),
            NETWORK_3 INT(10),            
            PLATFORM_2 INT(10),
            PLATFORM_3 INT(10),
            STORAGE_2 INT(10),
            PRIMARY KEY (HASH, ID_EXECUTION)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Logging (
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            HASH VARCHAR(255),
            ID_EXECUTION VARCHAR(255),
            APP_NAME VARCHAR(255),
            TIMESTAMP VARCHAR(255),
            TESTCASE VARCHAR(255),
            ERROR VARCHAR(255),
            PRIMARY KEY (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Permissions (
            HASH VARCHAR(255),
            ID_EXECUTION VARCHAR(255),
            APP_NAME VARCHAR(255),
            Permissions TEXT(20000),
            SUID VARCHAR (255),
            PRIMARY KEY (HASH, ID_EXECUTION)
        )
    ''')

def get_values_TestSSL_URLS(id_value):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = f"""SELECT * FROM TestSSL_URLS WHERE URL = %s"""

    try:
        cursor = cnx.cursor()
        cursor.execute(query, (id_value,))
        records = cursor.fetchall()

        return records
    except:
        return "failed"

def add_analyzed_app(apk_hash, uuid_execution, app_name, version_name, semgrep, script_version):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query_report = """INSERT INTO Report (HASH, ID_EXECUTION, APP_NAME, VERSION_NAME, SEMGREP, SCRIPT_VERSION, CODE_1, CODE_2, CRYPTO_1, CRYPTO_3, NETWORK_1, NETWORK_2, NETWORK_3, PLATFORM_2, PLATFORM_3, STORAGE_2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    query_total_fail_counts = """INSERT INTO Total_Fail_Counts (HASH, ID_EXECUTION, CODE_1, CODE_2, CRYPTO_1, CRYPTO_3, NETWORK_1, NETWORK_2, NETWORK_3, PLATFORM_2, PLATFORM_3, STORAGE_2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    try:    
        cursor.execute(query_report, (apk_hash, uuid_execution, app_name, version_name, semgrep, script_version, 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS'))
        cursor.execute(query_total_fail_counts, (apk_hash, uuid_execution, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        cnx.commit()
    except Exception as e:
        print(f'FAIL: {e}')
        return "failed"

def get_values_total_fail_counts(id_value, tests, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    tests_str = ', '.join(tests)
    query = f"""SELECT HASH, {tests_str} FROM Total_Fail_Counts WHERE HASH = %s and ID_EXECUTION = %s"""

    try:
        cursor = cnx.cursor()
        cursor.execute(query, (id_value, uuid_execution))
        records = cursor.fetchall()

        return records
    except:
        return "failed"

def get_all_uuid_executions():
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())
    
    query = f"""SELECT ID FROM Executions"""

    try:
        cursor = cnx.cursor()
        cursor.execute(query, )
        records = cursor.fetchall()
        ids = ""
        
        if records:
            ids = [record[0] for record in records]

        return ids

    except:
        return "failed"

def update_values(table, update_identifier, update_id_value, identifier, id_value, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = f"""UPDATE {table} SET {update_identifier} = %s WHERE {identifier} = %s and ID_EXECUTION = %s"""
    
    try:
        cursor.execute(query, (update_id_value, id_value, uuid_execution,))
        cnx.commit()
    except:
        print("Something Failed in table " + table)

def get_permissions_execution(uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = f"""SELECT HASH, APP_NAME, Permissions FROM Permissions WHERE ID_EXECUTION = %s"""

    try:
        cursor = cnx.cursor()
        cursor.execute(query, (uuid_execution))
        records = cursor.fetchall()

        return records
    except:
        return "failed"

def insert_values_logging(apk_hash, package_name, timestamp, tc, error, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """INSERT INTO Logging (HASH, APP_NAME, TIMESTAMP, TESTCASE, ERROR, ID_EXECUTION) VALUES (%s, %s, %s, %s, %s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash, package_name, timestamp, tc, error, uuid_execution))
        cnx.commit()
    except:
        return "failed"

def insert_new_finding(finding_data):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())
    
    query = """INSERT INTO Findings (HASH, APP_NAME, CATEGORY, CHECK_ID, PATH, LINE, ID_EXECUTION) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    
    try:    
        cursor.execute(query, tuple(finding_data))
        cnx.commit()
    except Exception as e:
        print(f'FAIL: {e}')
        return "failed"

def insert_new_report(report_data):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """INSERT INTO Report (HASH, ID_EXECUTION, APP_NAME, VERSION_NAME, SEMGREP, SCRIPT_VERSION, CODE_1, CODE_2, CRYPTO_1, CRYPTO_3, NETWORK_1, NETWORK_2, NETWORK_3, PLATFORM_2, PLATFORM_3, STORAGE_2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    try:    
        cursor.execute(query, tuple(report_data))
        cnx.commit()
    except Exception as e:
        print(f'FAIL: {e}')
        return "failed"

def insert_new_execution(uuid_execution, timestamp):

    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())
    
    query = """INSERT INTO Executions (ID, TIMESTAMP) VALUES (%s, %s)"""
    
    try:    
        cursor.execute(query, (uuid_execution, timestamp, ))
        cnx.commit()
    except Exception as e:
        print(f'FAIL: {e}')
        return "failed"

def insert_values_report(apk_hash, app_name, version_name, semgrep, script_version, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """INSERT INTO Report (HASH, APP_NAME, VERSION_NAME, SEMGREP, SCRIPT_VERSION, ID_EXECUTION) VALUES (%s, %s, %s, %s, %s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash, app_name, version_name, semgrep, script_version, uuid_execution))
        cnx.commit()
    except:
        return "failed"

def insert_values_permissions(apk_hash, package, permissions, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """INSERT INTO Permissions (HASH, APP_NAME, Permissions, ID_EXECUTION) VALUES (%s, %s, %s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash, package, permissions, uuid_execution,))
        cnx.commit()
    except:
        return "failed"

def update_values_permissions_add_suid(apk_hash, suid, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """UPDATE Permissions SET SUID = %s WHERE HASH = %s and ID_EXECUTION = %s"""
    
    try:    
        cursor.execute(query, (suid, apk_hash, uuid_execution))
        cnx.commit()
    except:
        return "failed"

def update_values_permissions_add_new_permissions_set(apk_hash, permissions, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """UPDATE Permissions SET Permissions = %s WHERE HASH = %s and ID_EXECUTION = %s"""
    
    try:    
        cursor.execute(query, (permissions, apk_hash, uuid_execution,))
        cnx.commit()
    except:
        return "failed"

def set_risk_score(uuid_execution, risk_score):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """UPDATE Executions SET RISK_SCORE = %s WHERE ID = %s"""
    
    try:
        cursor.execute(query, (risk_score, uuid_execution,))
        cnx.commit()
    except:
        print("Something Failed in table Executions")

def get_scanned_apks(uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = "SELECT count(*) FROM Report WHERE ID_EXECUTION = '" + uuid_execution + "'"


    try:
        cursor = cnx.cursor()
        cursor.execute(query)
        # Fetch the result
        count = cursor.fetchone()[0]
        
        return count
    except:
        return "failed"

def unify_suid_permissions(uuid_execution):
    all_perms = ""
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """SELECT * FROM Permissions WHERE ID_EXECUTION = %s"""
    query_single_app = """SELECT p.APP_NAME, p.Permissions FROM Permissions p WHERE p.APP_NAME = %s AND p.ID_EXECUTION = %s"""
    query_all_perms = """SELECT p.APP_NAME, p.Permissions, p.SUID FROM Permissions p WHERE SUID = %s AND p.ID_EXECUTION = %s"""
    
    try:
        cursor = cnx.cursor(buffered=False)
        cursor.execute(query, (uuid_execution,))
        records = cursor.fetchall()

        for row in records:
            app_name = row[2]
            app_SUID = row[4]
            if app_SUID is not None: # if SUID is set 
                if app_name != app_SUID: # if the package name is not the same as SUID, then append permissions
                    cursor.execute(query_single_app, (app_name, uuid_execution, ))
                    tuple_data = cursor.fetchall()[0]
                    current_perm = tuple_data[1]

                    cursor.execute(query_all_perms, (app_SUID, uuid_execution, ))
                    records_perm = cursor.fetchall()
                    for record in records_perm:
                        if record[0] != app_name and record[1] != "":
                            all_perms += "," + record[1]

                    current_perm += all_perms
                    joined_permissions = current_perm.split(',')

                    unique_permissions = [permission for i, permission in enumerate(joined_permissions) if permission not in joined_permissions[:i]]

                    result = ','.join(unique_permissions).rstrip(",").lstrip(",")

                    update_values_permissions_add_new_permissions_set(row[0], result, uuid_execution)

    except Exception as e:
        print("Failed while unifying permissions")
        return "failed"
    
def get_values_permissions(uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = "SELECT * FROM Permissions WHERE ID_EXECUTION = '" + uuid_execution + "'"

    try:
        cursor = cnx.cursor()
        cursor.execute(query)
        records = cursor.fetchall()

        return records
    except:
        return "failed"

def insert_values_total_fail_count(apk_hash, uuid_execution):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = f"""INSERT INTO Total_Fail_Counts (HASH, ID_EXECUTION) VALUES (%s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash, uuid_execution,))
        cnx.commit()
    except:
        return "failed"

def insert_values_testsslURLs(url, result):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + get_database_name())

    query = """INSERT INTO TestSSL_URLS (URL, RESULT) VALUES (%s, %s)"""
    
    try:    
        cursor.execute(query, (url, result))
        cnx.commit()
    except:
        return "failed"

def clear_database(database='automated_MASA'):
    cnx = mysql.connector.connect(host=DB_HOST_MASA, user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE ' + database)

    query_Report = '''DELETE FROM Report'''
    query_Permissions = '''DELETE FROM Permissions'''
    query_Total_Fail_Counts = '''DELETE FROM Total_Fail_Counts'''
    query_Logging = '''DELETE FROM Logging'''
    query_Findings = '''DELETE FROM Findings'''
    query_Executions = '''DELETE FROM Executions'''

    try:    
        cursor.execute(query_Report)
        cursor.execute(query_Permissions)
        cursor.execute(query_Total_Fail_Counts)
        cursor.execute(query_Logging)
        cursor.execute(query_Findings)
        cursor.execute(query_Executions)
        cnx.commit()
    except:
        print("Failed")

def get_database_name():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    database = config.get("database", {})

    return str(database)
