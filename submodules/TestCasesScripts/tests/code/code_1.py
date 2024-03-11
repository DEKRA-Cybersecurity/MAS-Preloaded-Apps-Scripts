from utils.auxiliar_functions import check_signature
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name, uuid_execution):

    verdict = 'FAIL'
    total_matches = 0

    with open(wdir+'/report_'+apk+'.txt', 'a+') as f:
        output_sign_count = 0
        signature_info = check_signature(wdir, apk, apk_hash, package_name, uuid_execution)

        for i in signature_info:
            if "v2): true" in i or "v3): true" in i:
                output_sign_count += 1
                
        if output_sign_count >= 1:
            verdict = 'PASS'
            database_utils.update_values("Report", "CODE_1", "PASS", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "CODE_1", total_matches, "HASH", apk_hash, uuid_execution)
            
        else:
            total_matches = 1
            database_utils.update_values("Report", "CODE_1", "FAIL", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "CODE_1", total_matches, "HASH", apk_hash, uuid_execution)

    print('CODE-1 successfully tested.')

    return [verdict, total_matches]

