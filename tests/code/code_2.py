from utils.auxiliar_functions import check_debuggable
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name):

    verdict = 'FAIL'

    debug_info = check_debuggable(wdir, apk_hash)

    with open(wdir+'/report_'+apk+'.txt', 'a+') as f:

        if debug_info == 'No relevant results':
            database_utils.update_values("Report", "CODE_2", "PASS", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", 0, "HASH", apk_hash)
            verdict = 'PASS'
            
        else:
            match_line = debug_info[0].decode().strip().split(':', 1)[0]
            database_utils.insert_new_dekra_finding(apk_hash, package_name, "CODE", "CODE-2", wdir+"/base/AndroidManifest.xml", match_line)
            database_utils.update_values("Report", "CODE_2", "FAIL", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", 1, "HASH", apk_hash)

        print('CODE-2 successfully tested.')

    return verdict