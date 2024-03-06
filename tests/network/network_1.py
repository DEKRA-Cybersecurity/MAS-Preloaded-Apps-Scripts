import subprocess
import datetime
import db.database_utils as database_utils
from utils.auxiliar_functions import get_suid_from_manifest

def check(wdir, apk, apk_hash, package_name, uuid_execution):
    '''
        Check if there is any URL with "http" schema.

        URLs are extracted from the static decompiled code.

        In the case there is at least one, it is INCONCLUSIVE (Manual review is required, as many of these URLs are static resources and not
        relevant to security purposes), otherwise, PASS.

        An auxiliar file with those found URLs is provided for manual review.

    '''
    verdict = 'FAIL'
    total_matches = 0
    with open(wdir+'/http_net2.txt') as f:
        lines = len(f.readlines())

    if lines > 0:
        try:
            http_location = wdir+"/http_net2.txt"

            cmd = ['python3', 'utils/check_network1_redirects.py', http_location]
            urls_found = subprocess.check_output(cmd, universal_newlines=True)
            total_matches = int(urls_found.strip())
            
            if total_matches == 0:
                database_utils.update_values("Report", "NETWORK_1", "PASS", "HASH", apk_hash, uuid_execution)
                database_utils.update_values("Total_Fail_Counts", "NETWORK_1", total_matches, "HASH", apk_hash, uuid_execution)
                verdict = 'PASS'
            else:
                database_utils.update_values("Report", "NETWORK_1", "FAIL", "HASH", apk_hash, uuid_execution)
                database_utils.update_values("Total_Fail_Counts", "NETWORK_1", total_matches, "HASH", apk_hash, uuid_execution)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                pass 
            else:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(apk_hash, package_name, ct, "NETWORK-1", "Check redirects script failed", uuid_execution)
                pass
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "NETWORK-1", "Check redirects script failed", uuid_execution)
            pass

    else:
        database_utils.update_values("Report", "NETWORK_1", "PASS", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "NETWORK_1", total_matches, "HASH", apk_hash, uuid_execution)
        verdict = 'PASS'

    print('NETWORK-1 successfully tested.')

    return [verdict, total_matches]
