import xml.etree.ElementTree as ET
from math import prod
import sys
sys.path.append('./')
from db import database_utils
import yaml

# Scoring dictionary

def extract_SUID(tree):
    root = tree.getroot()

    shared_user_id = root.get('{http://schemas.android.com/apk/res/android}sharedUserId')
    return shared_user_id

def extract_and_store_permissions(apk_hash, package_name, wdir):
    wdir = wdir+"/base/AndroidManifest.xml"
    tree = ET.parse(wdir)
    root = tree.getroot()
    scoring = get_scoring()
    # Extract permissions and calculate scores
    permissions = []
    scores = []
    for child in root.iter('uses-permission'):
        permission = child.attrib.get('{http://schemas.android.com/apk/res/android}name')
        if permission in scoring:
            permissions.append(permission)
            scores.append(scoring[permission])

    # Print the permissions and scores
    permissions_from_app = ','.join(str(x) for x in permissions)  #This is to upload the permissions to the table
    database_utils.insert_values_permissions(apk_hash, package_name, permissions_from_app)

    suid = extract_SUID(tree)
    if suid is not None:
        database_utils.update_values_permissions_add_suid(apk_hash, suid)

#FORMULA IS:
# All apps permission shall be extracted prior to formula calculation

'''
get_risk returns the risk associated to a permission, if that app holds a "risky" permission.
'''

def get_m_value(p, tests, actual_timestamp):
    total_fails = 0
    record_apps = database_utils.get_values_permissions(actual_timestamp)
    for rapp in record_apps:
        if p in rapp[2]:
            records = database_utils.get_values("Total_Fail_Counts", "HASH", rapp[0], tests)
            for r in records:
                for i in range(1,len(r)):
                    total_fails += r[i]

    return total_fails

def get_risk(p, permissions):
    scoring = get_scoring()
    if p in permissions:
        return scoring[p]
    else:
        return 0
    
'''
get_value_k returns the number of apps that holds permission p
'''
def get_value_k(p, actual_timestamp):
    total_apps = 0
    records = database_utils.get_values_permissions(actual_timestamp)
    for r in records:
        if p in r[2]:
            total_apps += 1

    return total_apps

def calculate_formula(Constant1, Constant2, tests, actual_timestamp):
    result = 0
    all_permissions = get_all_permissions()
    for p in all_permissions:
        risk = get_risk(p, all_permissions)  # Replace `get_risk(p)` with your specific risk calculation for each p
        value_k = get_value_k(p, actual_timestamp)  # Replace `get_value_k(p)` with your specific value K calculation for each p
        M = get_m_value(p, tests, actual_timestamp)
        term = risk * (1 - ((1 - Constant1) ** value_k) * ((1 - Constant2) ** M))

        result += term

    return round(result, 4)

def get_all_permissions():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    permissions_list = list(config['permissions'].keys())

    return permissions_list

def get_scoring():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    permissions_weights_dict = {permission: data['weight'] for permission, data in config['permissions'].items()}

    return permissions_weights_dict
