from utils.auxiliar_functions import check_debuggable
import db.database_utils as database_utils

def check(wdir, name, apk_hash):
    debug_info = check_debuggable(wdir, apk_hash)
    with open(wdir+'/report_'+name+'.txt', 'a+') as f:
        if debug_info == 'No relevant results':
            database_utils.update_values("Report", "CODE_2", "Pass", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", 0, "HASH", apk_hash)
        else:
            database_utils.update_values("Report", "CODE_2", "Fail", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", 1, "HASH", apk_hash)
        print('CODE-2 successfully tested.')