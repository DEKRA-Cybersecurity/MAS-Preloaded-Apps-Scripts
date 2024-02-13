import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name):
    '''
        Check for potentially vulnerable algorithms in the code.
        If a match is found, FAIL is set, otherwise PASS
    '''
    verdict = 'FAIL'
    total_matches = 0
    vuln_algo = ["\"AES/CBC/PKCS5Padding\"", "\"DES/CBC/PKCS5Padding\"", "\".*/ECB/.*\"", "\"^(TLS).*-CBC-.*\""]

    for i in vuln_algo:
        cmd = f"grep -rnw --exclude='*.dex' -e {i} {wdir}/decompiled/sources"
        set_matches = set()
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if len(output) > 0:
                for match in output:
                    match_str = match.decode()
                    try:
                        if '.java' in match_str:
                            match_file = match_str.split(":")[0]
                            match_line = match_str.split(":")[1] 
                            set_matches.add(match_file)
                            database_utils.insert_new_dekra_finding(apk_hash, package_name, "CRYPTO", "CRYPTO-3", match_file, match_line)
                        else:
                            set_matches.add(match_str)
                            database_utils.insert_new_dekra_finding(apk_hash, package_name, "CRYPTO", "CRYPTO-3", match_str, '-')
                    except:
                        print('[ERROR] It was not possible to get match_file or match_line')
            total_matches += len(set_matches)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                pass 
            else:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(apk_hash, ct, "CRYPTO-3", f"grep command failed for {i}")
                pass #No output
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "CRYPTO-3", f"grep command failed for {i}")
            pass #No output

    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_3", "FAIL", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "CRYPTO_3", "PASS", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", 0, "HASH", apk_hash)
        verdict = 'PASS'

    print('CRYPTO-3 successfully tested.')

    return verdict