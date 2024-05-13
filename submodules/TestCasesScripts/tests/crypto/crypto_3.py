import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name, uuid_execution):
    '''
        Check for potentially vulnerable algorithms in the code.
        If a match is found, FAIL is set, otherwise PASS
    '''
    verdict = 'FAIL'
    total_matches = 0
    vuln_algo = ["\"AES/CBC/PKCS5Padding\"", "\"DES/CBC/PKCS5Padding\"", "\".*\\/ECB\"", "\"^(TLS).*-CBC-.*\""]
    
    for i in vuln_algo:
        cmd = f"grep -rnws --exclude='*.dex' -E {i} {wdir}/decompiled/sources"
        
        try:
            output = subprocess.check_output(cmd, shell=True, timeout=200).splitlines()
            
            if len(output) > 0:
                for match in output:
                    match_str = match.decode()
                    try:
                        if '.java' in match_str:
                            match_file = match_str.split(":")[0]
                            match_line = match_str.split(":")[1] 
                            total_matches += 1
                            database_utils.insert_new_finding([apk_hash, package_name, "CRYPTO", "CRYPTO-3", match_file, match_line, uuid_execution])
                        else:
                            total_matches += 1
                            database_utils.insert_new_finding([apk_hash, package_name, "CRYPTO", "CRYPTO-3", match_str, '-', uuid_execution])
                    except:
                        print('[ERROR] It was not possible to get match_file or match_line')
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                pass 
            else:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(apk_hash, package_name, ct, "CRYPTO-3", f"grep command failed due to {wdir}/decompiled/sources does not exists", uuid_execution)
                pass #No output
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "CRYPTO-3", f"grep command failed for {i}", uuid_execution)
            pass #No output

    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_3", "FAIL", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", total_matches, "HASH", apk_hash, uuid_execution)
    else:
        verdict = 'PASS'
        database_utils.update_values("Report", "CRYPTO_3", "PASS", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", total_matches, "HASH", apk_hash, uuid_execution)

    print('CRYPTO-3 successfully tested.')

    return [verdict, total_matches]
