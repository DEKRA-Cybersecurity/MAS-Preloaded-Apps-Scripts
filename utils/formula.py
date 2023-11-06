import xml.etree.ElementTree as ET
from math import prod
import sys
sys.path.append('./')
from db import database_utils

# Scoring dictionary

all_permissions = [
    'android.permission.INSTALL_PACKAGES',
    'android.permission.COPY_PROTECTED_DATA', 
    'android.permission.WRITE_SECURE_SETTINGS', 
    'android.permission.READ_FRAME_BUFFER', 
    'android.permission.MANAGE_CA_CERTIFICATES', 
    'android.permission.MANAGE_APP_OPS_MODES', 
    'android.permission.GRANT_RUNTIME_PERMISSIONS', 
    'android.permission.DUMP', 
    'android.permission.CAMERA', 
    'android.permission.SYSTEM_CAMERA', 
    'android.permission.MANAGE_PROFILE_AND_DEVICE_OWNERS', 
    'android.permission.MOUNT_UNMOUNT_FILESYSTEMS', 
    'android.permission.INSTALL_GRANT_RUNTIME_PERMISSIONS', 
    'android.permission.READ_SMS', 
    'android.permission.WRITE_SMS', 
    'android.permission.RECEIVE_MMS', 
    'android.permission.SEND_SMS_NO_CONFIRMATION', 
    'android.permission.RECEIVE_SMS', 
    'android.permission.READ_LOGS', 
    'android.permission.READ_PRIVILEGED_PHONE_STATE', 
    'android.permission.LOCATION_HARDWARE', 
    'android.permission.ACCESS_FINE_LOCATION', 
    'android.permission.ACCESS_BACKGROUND_LOCATION', 
    'android.permission.BIND_ACCESSIBILITY_SERVICE', 
    'android.permission.ACCESS_WIFI_STATE', 
    'com.android.voicemail.permission.READ_VOICEMAIL', 
    'android.permission.RECORD_AUDIO', 
    'android.permission.CAPTURE_AUDIO_OUTPUT', 
    'android.permission.ACCESS_NOTIFICATIONS', 
    'android.permission.INTERACT_ACROSS_USERS_FULL', 
    'android.permission.BLUETOOTH_PRIVILEGED', 
    'android.permission.GET_PASSWORD', 
    'android.permission.INTERNAL_SYSTEM_WINDOW', 
    'android.permission.ACCESS_COARSE_LOCATION', 
    'android.permission.CHANGE_COMPONENT_ENABLED_STATE', 
    'android.permission.READ_CONTACTS', 
    'android.permission.WRITE_CONTACTS', 
    'android.permission.CONNECTIVITY_INTERNAL', 
    'android.permission.ACCESS_MEDIA_LOCATION', 
    'android.permission.READ_EXTERNAL_STORAGE', 
    'android.permission.WRITE_EXTERNAL_STORAGE', 
    'android.permission.SYSTEM_ALERT_WINDOW', 
    'android.permission.READ_CALL_LOG', 
    'android.permission.WRITE_CALL_LOG', 
    'android.permission.INTERACT_ACROSS_USERS', 
    'android.permission.MANAGE_USERS', 
    'android.permission.READ_CALENDAR', 
    'android.permission.BLUETOOTH_ADMIN', 
    'android.permission.BODY_SENSORS', 
    'android.permission.DOWNLOAD_WITHOUT_NOTIFICATION', 
    'android.permission.PACKAGE_USAGE_STATS', 
    'android.permission.MASTER_CLEAR', 
    'android.permission.DELETE_PACKAGES', 
    'android.permission.GET_PACKAGE_SIZE', 
    'android.permission.BLUETOOTH', 
    'android.permission.DEVICE_POWER', 
    'android.permission.ACCESS_NETWORK_STATE', 
    'android.permission.RECEIVE_BOOT_COMPLETED', 
    'android.permission.WAKE_LOCK', 
    'android.permission.FLASHLIGHT', 
    'android.permission.VIBRATE', 
    'android.permission.WRITE_MEDIA_STORAGE', 
    'android.permission.MODIFY_AUDIO_SETTINGS']
  
scoring = {
    "android.permission.INSTALL_PACKAGES": 100,
    "android.permission.COPY_PROTECTED_DATA": 10,
    "android.permission.WRITE_SECURE_SETTINGS": 10,
    "android.permission.READ_FRAME_BUFFER": 10,
    "android.permission.MANAGE_CA_CERTIFICATES": 10,
    "android.permission.MANAGE_APP_OPS_MODES": 10,
    "android.permission.GRANT_RUNTIME_PERMISSIONS": 10,
    "android.permission.DUMP": 10,
    "android.permission.CAMERA": 10,
    "android.permission.SYSTEM_CAMERA": 10,
    "android.permission.MANAGE_PROFILE_AND_DEVICE_OWNERS": 10,
    "android.permission.MOUNT_UNMOUNT_FILESYSTEMS": 10,
    "android.permission.INSTALL_GRANT_RUNTIME_PERMISSIONS": 7.5,
    "android.permission.READ_SMS": 7.5,
    "android.permission.WRITE_SMS": 7.5,
    "android.permission.RECEIVE_MMS": 7.5,
    "android.permission.SEND_SMS_NO_CONFIRMATION": 7.5,
    "android.permission.RECEIVE_SMS": 7.5,
    "android.permission.READ_LOGS": 7.5,
    "android.permission.READ_PRIVILEGED_PHONE_STATE": 7.5,
    "android.permission.LOCATION_HARDWARE": 7.5,
    "android.permission.ACCESS_FINE_LOCATION": 7.5,
    "android.permission.ACCESS_BACKGROUND_LOCATION": 7.5,
    "android.permission.BIND_ACCESSIBILITY_SERVICE": 7.5,
    "android.permission.ACCESS_WIFI_STATE": 7.5,
    "com.android.voicemail.permission.READ_VOICEMAIL": 7.5,
    "android.permission.RECORD_AUDIO": 7.5,
    "android.permission.CAPTURE_AUDIO_OUTPUT": 7.5,
    "android.permission.ACCESS_NOTIFICATIONS": 7.5,
    "android.permission.INTERACT_ACROSS_USERS_FULL": 7.5,
    "android.permission.BLUETOOTH_PRIVILEGED": 7.5,
    "android.permission.GET_PASSWORD": 7.5,
    "android.permission.INTERNAL_SYSTEM_WINDOW": 7.5,
    "android.permission.ACCESS_COARSE_LOCATION": 5,
    "android.permission.CHANGE_COMPONENT_ENABLED_STATE": 5,
    "android.permission.READ_CONTACTS": 5,
    "android.permission.WRITE_CONTACTS": 5,
    "android.permission.CONNECTIVITY_INTERNAL": 5,
    "android.permission.ACCESS_MEDIA_LOCATION": 5,
    "android.permission.READ_EXTERNAL_STORAGE": 5,
    "android.permission.WRITE_EXTERNAL_STORAGE": 5,
    "android.permission.SYSTEM_ALERT_WINDOW": 5,
    "android.permission.READ_CALL_LOG": 5,
    "android.permission.WRITE_CALL_LOG": 5,
    "android.permission.INTERACT_ACROSS_USERS": 5,
    "android.permission.MANAGE_USERS": 5,
    "android.permission.READ_CALENDAR": 5,
    "android.permission.BLUETOOTH_ADMIN": 5,
    "android.permission.BODY_SENSORS": 5,
    "android.permission.DOWNLOAD_WITHOUT_NOTIFICATION": 2.5,
    "android.permission.PACKAGE_USAGE_STATS": 2.5,
    "android.permission.MASTER_CLEAR": 2.5,
    "android.permission.DELETE_PACKAGES": 2.5,
    "android.permission.GET_PACKAGE_SIZE": 2.5,
    "android.permission.BLUETOOTH": 2.5,
    "android.permission.DEVICE_POWER": 2.5,
    "android.permission.ACCESS_NETWORK_STATE": 0,
    "android.permission.RECEIVE_BOOT_COMPLETED": 0,
    "android.permission.WAKE_LOCK": 0,
    "android.permission.FLASHLIGHT": 0,
    "android.permission.VIBRATE": 0,
    "android.permission.WRITE_MEDIA_STORAGE": 0,
    "android.permission.MODIFY_AUDIO_SETTINGS": 0,
}

def extract_SUID(tree):
    root = tree.getroot()

    shared_user_id = root.get('{http://schemas.android.com/apk/res/android}sharedUserId')
    return shared_user_id


def extract_and_store_permissions(app_hash, package, wdir):
    tree = ET.parse(wdir)
    root = tree.getroot()
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
    database_utils.insert_values_permissions(app_hash, package, permissions_from_app)

    suid = extract_SUID(tree)
    if suid is not None:
        database_utils.update_values_permissions_add_suid(app_hash, suid)

#FORMULA IS:
# All apps permission shall be extracted prior to formula calculation

'''
get_risk returns the risk associated to a permission, if that app holds a "risky" permission.
'''

def get_m_value(p):
    total_fails = 0
    record_apps = database_utils.get_values_permissions()
    for rapp in record_apps:
        if p in rapp[2]:
            records = database_utils.get_values("Total_Fail_Counts", "HASH", rapp[0])
            for r in records:
                for i in range(1,len(r)):
                    total_fails += r[i]

    return total_fails

def get_risk(p, permissions):
    if p in permissions:
        return scoring[p]
    else:
        return 0
    
'''
get_value_k returns the number of apps that holds permission p
'''
def get_value_k(p):
    total_apps = 0
    records = database_utils.get_values_permissions()
    for r in records:
        if p in r[2]:
            total_apps += 1

    return total_apps


def calculate_formula(Constant1, Constant2):
    result = 0

    for p in all_permissions:
        risk = get_risk(p, all_permissions)  # Replace `get_risk(p)` with your specific risk calculation for each p
        value_k = get_value_k(p)  # Replace `get_value_k(p)` with your specific value K calculation for each p
        M = get_m_value(p)
        term = risk * (1 - ((1 - Constant1) ** value_k) * ((1 - Constant2) ** M))

        result += term

    return result
