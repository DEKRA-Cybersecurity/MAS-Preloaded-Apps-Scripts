import xml.etree.ElementTree as ET
import db.database_utils as database_utils
import re, os

def check(wdir, apk, apk_hash, package_name):
    '''
    Extract custom url from the application.

    It extracts the scheme and the path defined. However, for this version it counts the number of custom URL scheme found
    to filter out those applications that have no custom URL in place.
    '''
    verdict = 'PASS'
    manifest_path = os.path.join(wdir, 'base/AndroidManifest.xml')
    custom_urls = 0

    with open(manifest_path, 'r') as file:
        xml_data = file.read()
        pattern = r'android:scheme="([^"]+)"'
        scheme_values = re.findall(pattern, xml_data)

        for value in scheme_values:
            if(value != 'http' and value != 'https' and value != '' and value != None):
                custom_urls = custom_urls + 1
                                                
    if custom_urls > 0:
        database_utils.update_values("Report", "PLATFORM_3", "Needs Review", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_3", custom_urls, "HASH", apk_hash)
        verdict = 'Needs Review'
    else:
        database_utils.update_values("Report", "PLATFORM_3", "PASS", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_3", 0, "HASH", apk_hash)

    print('PLATFORM-3 successfully tested.')

    return verdict
