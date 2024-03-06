from utils.auxiliar_functions import check_debuggable
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name, uuid_execution):

    verdict = 'FAIL'
    total_matches = 0

    debug_info = check_debuggable(wdir, apk_hash, package_name, uuid_execution)

    with open(wdir+'/report_'+apk+'.txt', 'a+') as f:

        if debug_info == 'No relevant results':
            verdict = 'PASS'
            database_utils.update_values("Report", "CODE_2", "PASS", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", total_matches, "HASH", apk_hash, uuid_execution)
            
        else:
            total_matches = 1
            match_line = debug_info[0].decode().strip().split(':', 1)[0]
            database_utils.insert_new_finding([apk_hash, package_name, "CODE", "CODE-2", wdir+"/base/AndroidManifest.xml", match_line, uuid_execution])
            database_utils.update_values("Report", "CODE_2", "FAIL", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", total_matches, "HASH", apk_hash, uuid_execution)

        print('CODE-2 successfully tested.')

    return [verdict, total_matches] 