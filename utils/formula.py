import xml.etree.ElementTree as ET
from math import prod
import sys
sys.path.append('./')
from db import database_utils
# from settings import SUID_SYSTEM
import yaml

# Scoring dictionary

def extract_SUID(tree):
    root = tree.getroot()

    shared_user_id = root.get('{http://schemas.android.com/apk/res/android}sharedUserId')
    return shared_user_id

def extract_and_store_permissions(apk_hash, package_name, wdir, uuid_execution):
    wdir = wdir+"/base/AndroidManifest.xml"
    tree = ET.parse(wdir)
    root = tree.getroot()
    suid = extract_SUID(tree)
    all_perms = set()
    android_ns = 'http://schemas.android.com/apk/res/android'

    # Extract permissions
    for elem in root.iter():
        if elem.tag == 'permission' or elem.tag == 'uses-permission':
            name = elem.get(f'{{{android_ns}}}name')
            if name:
                all_perms.add(name)

    # if suid == SUID_SYSTEM:
    #     perms_config = get_all_permissions()
    #     all_perms.update(perms_config)

    # Print the permissions and scores
    permissions_from_app = ','.join(str(x) for x in all_perms)  #This is to upload the permissions to the table
    database_utils.insert_values_permissions(apk_hash, package_name, permissions_from_app, uuid_execution)
    if suid is not None:
        database_utils.update_values_permissions_add_suid(apk_hash, suid, uuid_execution)

#FORMULA IS:
# All apps permission shall be extracted prior to formula calculation

'''
get_risk returns the risk associated to a permission, if that app holds a "risky" permission.
'''


def get_m_value(perm, tests, uuid_execution):
    total_fails = 0
    record_apps = database_utils.get_values_permissions(uuid_execution)
    for rapp in record_apps:
        permissions_list = get_permissions_list(rapp[3])
        if perm in permissions_list:
            records = database_utils.get_values_total_fail_counts(rapp[0], tests, uuid_execution)
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
def get_value_k(perm, uuid_execution):
    total_apps = 0
    records = database_utils.get_values_permissions(uuid_execution)
    for row in records:
        permissions_list = get_permissions_list(row[3])
        if perm in permissions_list:
            total_apps += 1

    return total_apps

def calculate_formula(Constant1, Constant2, tests, uuid_execution):
    result = 0
    all_permissions = get_all_permissions()
    for p in all_permissions:
        risk = get_risk(p, all_permissions)
        value_k = get_value_k(p, uuid_execution)
        M = get_m_value(p, tests, uuid_execution)
        term = risk * (1 - ((1 - Constant1) ** value_k) * ((1 - Constant2) ** M))

        result += term

    formula_value = round(result, 4)
    sum_weights = get_sum_weights()

    risk_score = (formula_value / sum_weights) * 100

    database_utils.set_risk_score(uuid_execution, risk_score)

    return risk_score


def get_android_version():
    try:
        with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        android_version = int(config.get("androidVersion", 0))
        return android_version

    except:
        print("Error while getting android version from config file.")
        return 0
    
def get_p_value():
    try:
        with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        p_value = float(config.get("formula_p", 0))
        return p_value

    except:
        print("Error while getting p value from config file.")
        return 0
    
def get_q_value():
    try:
        with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        q_value = float(config.get("formula_q", 0))
        return q_value

    except:
        print("Error while getting q value from config file.")
        return 0


def get_all_permissions():

    android_version = get_android_version()

    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    permissions_list = []
    if config['permissions'][android_version]:
        permissions_list = list(config['permissions'][android_version].keys())

    return permissions_list


def get_scoring():

    android_version = get_android_version()

    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    permissions_weights_dict = {}
    if config['permissions'][android_version]:
        permissions_weights_dict = {permission: data['weight'] for permission, data in config['permissions'][android_version].items()}

    return permissions_weights_dict


def get_permissions_list(permissions_str):
    if permissions_str:
        permissions_list = [element.strip() for element in permissions_str.split(
            ",")] if permissions_str else []

        return permissions_list

    return []

def get_sum_weights():

    android_version = get_android_version()

    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    total_weight = 0

    permissions = config.get('permissions', {})
    if android_version in permissions:
        version_permissions = permissions[android_version] 
        for key, value in version_permissions.items():
            total_weight += value.get('weight', 0)
    else:
        print('The Android version you have specified in the config file does not have an associated permissions list.')

    return total_weight
