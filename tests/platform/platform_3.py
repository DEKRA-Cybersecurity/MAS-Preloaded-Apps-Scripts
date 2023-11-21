import xml.etree.ElementTree as ET
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name):
    '''
    Extract custom url from the application.

    It extracts the scheme and the path defined. However, for this version it counts the number of custom URL scheme found
    to filter out those applications that have no custom URL in place.
    '''
    verdict = 'PASS'
    root = ET.parse(f'{wdir}/base/AndroidManifest.xml').getroot()
    activity_urls_dict = {}

    for app in root.findall("application"):
        for activity in app.iter("activity"):

            i_filters = [x for x in activity.iter("intent-filter")] 
            
            if len(i_filters) > 0:

                custom_urls = []

                for i_filter in i_filters:
                    for data  in i_filter.iter("data"):
                        host = ''
                        path = ''
                        scheme = ''

                        for x in data.attrib.keys():
                            
                            if "host" in x:
                                host=data.attrib[x]
                            if "path" in x:
                                path=data.attrib[x]
                            
                            if "scheme" in x:
                                scheme=data.attrib[x]

                            if scheme != '' and scheme != 'http' and scheme != 'https':
                                custom_urls.append(f'{scheme}://{host}{path}')

                                
                custom_urls = list(dict.fromkeys(custom_urls))
                

                if len(custom_urls) > 0:
                    for i in activity.attrib.keys():
                        if "name" in i:
                            activity_urls_dict[activity.attrib[i]] = custom_urls             
                                                 
    if len(activity_urls_dict) > 0:
        database_utils.update_values("Report", "PLATFORM_3", "Needs Review", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_3", 0, "HASH", apk_hash)
        verdict = 'Needs Review'
    else:
        database_utils.update_values("Report", "PLATFORM_3", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_3", 0, "HASH", apk_hash)

    print('PLATFORM-3 successfully tested.')

    return verdict
