import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk_hash):
    '''
        Check for potentially vulnerable algorithms in the code.
        If a match is found, FAIL is set, otherwise PASS
    '''
    total_matches = 0
    vuln_algo = ["\"AES/CBC/PKCS5Padding\"", "\"DES/CBC/PKCS5Padding\"", "\".*/ECB/.*\"", "\"^(TLS).*-CBC-.*\""]

    for i in vuln_algo:
        cmd = f"grep -rlnwz -e {i} {wdir}/decompiled | wc -l"
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if int(output[0]) > 0:
                total_matches += int(output[0])
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "CRYPTO-3", f"grep command failed for {i}")
            pass #No output

    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_3", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "CRYPTO_3", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", 0, "HASH", apk_hash)
    print('CRYPTO-3 successfully tested.')