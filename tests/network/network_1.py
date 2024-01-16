import subprocess
import datetime
import db.database_utils as database_utils
from utils.auxiliar_functions import get_suid_from_manifest

def check(wdir, apk, apk_hash, package_name):
    '''
        Check if there is any URL with "http" schema.

        URLs are extracted from the static decompiled code.

        In the case there is at least one, it is INCONCLUSIVE (Manual review is required, as many of these URLs are static resources and not
        relevant to security purposes), otherwise, PASS.

        An auxiliar file with those found URLs is provided for manual review.

    '''
    verdict = 'FAIL'
    with open(wdir+'/http_net2.txt') as f:
        lines = len(f.readlines())

    if lines > 0:
        try:
            cmd = f'utils/check_network1_redirects.sh {wdir+"/http_net2.txt"}'
            output = subprocess.check_output(cmd, shell=True)
            if output.decode("utf-8").rstrip("\n") == "PASS":
                database_utils.update_values(
                    "Report", "NETWORK_1", "PASS", "HASH", apk_hash)
                database_utils.update_values(
                    "Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash)
                verdict = 'PASS'
            else:
                database_utils.update_values(
                    "Report", "NETWORK_1", "FAIL", "HASH", apk_hash)
                database_utils.update_values(
                    "Total_Fail_Counts", "NETWORK_1", 1, "HASH", apk_hash)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                pass 
            else:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(
                    apk_hash, ct, "NETWORK-1", "Check redirects script failed")
                pass
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(
                apk_hash, ct, "NETWORK-1", "Check redirects script failed")
            pass

    else:
        database_utils.update_values(
            "Report", "NETWORK_1", "PASS", "HASH", apk_hash)
        database_utils.update_values(
            "Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash)
        verdict = 'PASS'

    print('NETWORK-1 successfully tested.')

    return verdict
