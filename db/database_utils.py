import mysql.connector
from settings import DB_USER_MASA, DB_PASSWORD_MASA

def first_execution():
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()

    cursor.execute('CREATE DATABASE automated_MASA')

    cursor.execute('USE automated_MASA')

    cursor.execute('''
        CREATE TABLE TestSSL_URLS (
            URL VARCHAR(255) PRIMARY KEY,
            RESULT VARCHAR(255)
        )
    ''')

    cursor.execute('''
        CREATE TABLE HTTP_URLS (
            URL VARCHAR(255) PRIMARY KEY
        )
    ''')

    cursor.execute('''
        CREATE TABLE Report (
            HASH VARCHAR(255) PRIMARY KEY,
            APP_NAME VARCHAR(255),
            CODE_1 VARCHAR(255),
            CODE_2 VARCHAR(255),
            CRYPTO_1 VARCHAR(255),
            CRYPTO_3 VARCHAR(255),
            NETWORK_1 VARCHAR(255),
            NETWORK_2 VARCHAR(255),
            NETWORK_3 VARCHAR(255),
            PLATFORM_2 VARCHAR(255),
            PLATFORM_3 VARCHAR(255),
            STORAGE_2 VARCHAR(255)            
        )
    ''')

    cursor.execute('''
        CREATE TABLE Total_Fail_Counts (
            HASH VARCHAR(255) PRIMARY KEY,
            CODE_1 INT(10),
            CODE_2 INT(10),
            CRYPTO_1 INT(10),
            CRYPTO_3 INT(10),
            NETWORK_1 INT(10),
            NETWORK_2 INT(10),
            NETWORK_3 INT(10),            
            PLATFORM_2 INT(10),
            PLATFORM_3 INT(10),
            STORAGE_2 INT(10)            
        )
    ''')

    cursor.execute('''
        CREATE TABLE Logging (
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            HASH VARCHAR(255),
            TIMESTAMP VARCHAR(255),
            TESTCASE VARCHAR(255),
            ERROR VARCHAR(255),
            PRIMARY KEY (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Total_Counts (
            HASH VARCHAR(255) PRIMARY KEY,
            Fail INT(10),
            Pass INT(10),
            Needs_Review INT(10)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Permissions (
            HASH VARCHAR(255) PRIMARY KEY,
            APP_NAME VARCHAR(255),
            Permissions TEXT(20000),
            SUID VARCHAR (255)
        )
    ''')

def get_values(table, identifier, id_value, tests):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    tests_str = ', '.join(tests)

    if tests == None:
        query = f"""SELECT * FROM {table} WHERE {identifier} = %s"""
    else:
        query = f"""SELECT HASH, {tests_str} FROM {table} WHERE {identifier} = %s"""

    try:
        cursor = cnx.cursor()
        cursor.execute(query, (id_value,))
        records = cursor.fetchall()

        return records
    except:
        return "failed"
    '''
    To iterate through these values:
        for row in records:
            row[0] -- first column
            row[1] -- second column
            ...
    '''

def update_values(table, update_identifier, update_id_value, identifier, id_value):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = f"""UPDATE {table} SET {update_identifier} = %s WHERE {identifier} = %s"""
    
    try:
        cursor.execute(query, (update_id_value, id_value))
        cnx.commit()
        return "success"
    except:
        print("Something Failed in table " + table)
        return "failed"

def insert_values_logging(apk_hash, timestamp, tc, error):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """INSERT INTO Logging (HASH, TIMESTAMP, TESTCASE, ERROR) VALUES (%s, %s, %s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash,timestamp, tc, error))
        cnx.commit()
        return "success"
    except:
        return "failed"

def insert_values_report(apk_hash, app_name):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """INSERT INTO Report (HASH, APP_NAME) VALUES (%s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash, app_name))
        cnx.commit()
        return "success"
    except:
        return "failed"
    
def insert_values_permissions(apk_hash, package, permissions):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """INSERT INTO Permissions (HASH, APP_NAME, Permissions) VALUES (%s, %s, %s)"""
    
    try:    
        cursor.execute(query, (apk_hash, package, permissions))
        cnx.commit()
        return "success"
    except:
        return "failed"

def update_values_permissions_add_suid(apk_hash, suid):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """UPDATE Permissions SET SUID = %s WHERE HASH = %s"""
    
    try:    
        cursor.execute(query, (suid, apk_hash))
        cnx.commit()
        return "success"
    except:
        return "failed"

def update_values_permissions_add_new_permissions_set(apk_hash, permissions):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """UPDATE Permissions SET Permissions = %s WHERE HASH = %s"""
    
    try:    
        cursor.execute(query, (permissions, apk_hash))
        cnx.commit()
        return "success"
    except:
        return "failed"

def unify_suid_permissions():
    all_perms = ""
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """SELECT * FROM Permissions"""
    query_single_app = """SELECT APP_NAME, Permissions FROM Permissions WHERE APP_NAME = %s"""
    query_all_perms = """SELECT APP_NAME, Permissions, SUID FROM Permissions WHERE SUID = %s"""

    try:
        cursor = cnx.cursor(buffered=False)
        cursor.execute(query)
        records = cursor.fetchall()

        for row in records:
            if row[3] is not None: #if SUID is set 
                if row[1] != row[3]: #if the package name is not the same as SUID, then append permissions
                    cursor.execute(query_single_app, (row[1],))
                    current_perm = cursor.fetchall()[0][1]

                    cursor.execute(query_all_perms, (row[3],))
                    records_perm = cursor.fetchall()
                    for record in records_perm:
                        if record[0] != row[1] and record[1] != "":
                            all_perms += "," + record[1]


                    current_perm += all_perms
                    joined_permissions = current_perm.split(',')

                    unique_permissions = [permission for i, permission in enumerate(joined_permissions) if permission not in joined_permissions[:i]]

                    result = ','.join(unique_permissions).rstrip(",").lstrip(",")

                    update_values_permissions_add_new_permissions_set(row[0], result)

    except:
        print("Failed while unifying permissions")
        return "failed"
    
def get_values_permissions():
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = f"""SELECT * FROM Permissions"""

    try:
        cursor = cnx.cursor()
        cursor.execute(query)
        records = cursor.fetchall()

        return records
    except:
        return "failed"
    '''
    To iterate through these values:
        for row in records:
            row[0] -- first column
            row[1] -- second column
            ...
    '''

def insert_values_total_fail_count(apk_hash):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = f"""INSERT INTO Total_Fail_Counts (HASH) VALUES (%s)"""
    
    try:    
        cursor.execute(query, (apk_hash,))
        cnx.commit()
        return "success"
    except:
        return "failed"

def insert_values_testsslURLs(url, result):
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query = """INSERT INTO TestSSL_URLS (URL, RESULT) VALUES (%s, %s)"""
    
    try:    
        cursor.execute(query, (url, result))
        cnx.commit()
        return "success"
    except:
        return "failed"

def clear_database():
    cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
    cursor = cnx.cursor()
    cursor.execute('USE automated_MASA')

    query_Report = '''DELETE FROM Report'''
    query_Permissions = '''DELETE FROM Permissions'''
    query_Total_Fail_Counts = '''DELETE FROM Total_Fail_Counts'''

    try:    
        cursor.execute(query_Report)
        cursor.execute(query_Permissions)
        cursor.execute(query_Total_Fail_Counts)
        cnx.commit()
    except:
        print("Failed")