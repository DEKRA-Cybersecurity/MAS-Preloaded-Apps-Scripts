from utils.auxiliar_functions import check_signature
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name):
    verdict = 'FAIL'
    with open(wdir+'/report_'+apk+'.txt', 'a+') as f:
        output_sign_count = 0
        signature_info = check_signature(wdir, apk, apk_hash)

        for i in signature_info:
            if "v2): true" in i or "v3): true" in i:
                output_sign_count += 1
                
        if output_sign_count >= 1:
            database_utils.update_values("Report", "CODE_1", "PASS", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_1", 0, "HASH", apk_hash)
            verdict = 'PASS'

        else:
            database_utils.update_values("Report", "CODE_1", "FAIL", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_1", 0, "HASH", apk_hash)

    print('CODE-1 successfully tested.')

    return verdict