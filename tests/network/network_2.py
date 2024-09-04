import subprocess
import datetime
import db.database_utils as database_utils
from settings import PATH_TESTSSL
from utils.auxiliar_functions import get_suid_from_manifest, remove_last_backslash

def check(wdir, apk, apk_hash, package_name, uuid_execution):
    '''
        Check for potentially vulnerable TLS configurations.
        If a match is found, INCONCLUSIVE is set, could be a potential FAIL
        This case creates a report that shall be reviewed manually to inspect for a verdict in the Test Case

        Future work: check with a whitelist of URLs if they are considered PASS even if they allow TLS1 or TLS1.1 according to ciphersuites.
    '''
    verdict = 'PASS'
    total_matches = 0
    is_inconclusive = False
    grep_filter = "\"((TLSv1:)|(TLSv1.1:)).*(-DES-[A-Z0-9]+)\""
    with open(wdir+'/_filtered_net2.txt') as all_urls:

        for url in all_urls:
            url_total_match = 0
            url_no_breakline = url.rstrip("\n")
            final_url = remove_last_backslash(url_no_breakline)
            cmd = f'echo no | {PATH_TESTSSL} -P {final_url} 2>/dev/null | grep -E {grep_filter} | wc -l'

            results = database_utils.get_values_TestSSL_URLS(url_no_breakline)
            
            if not results:
                try:
                    output = subprocess.check_output(cmd, shell=True).splitlines()
                    if int(output[0]) > 0:
                        total_matches += 1
                        url_total_match = 1
                except subprocess.CalledProcessError as e:
                    if e.returncode == 1:
                        pass 
                    else:
                        ct = datetime.datetime.now()
                        database_utils.insert_values_logging(apk_hash, package_name, ct, "NETWORK-2", "Command failed.", uuid_execution)
                        pass  # No output
                except:
                    ct = datetime.datetime.now()
                    database_utils.insert_values_logging(apk_hash, package_name, ct, "NETWORK-2", "Command failed.", uuid_execution)
                    pass  # No output

                if url_total_match > 0:
                    is_inconclusive = True
                    database_utils.insert_values_testsslURLs(url_no_breakline, "Needs Review")
                else:
                    database_utils.insert_values_testsslURLs(url_no_breakline, "Pass")

            elif not is_inconclusive and results[0][1] == "Needs Review":
                    is_inconclusive = True
                    total_matches += 1

    if is_inconclusive:
        database_utils.update_values("Report", "NETWORK_2", "Needs Review", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "NETWORK_2", total_matches, "HASH", apk_hash, uuid_execution)
        verdict = 'Needs Review'
    else:
        total_matches = 0
        database_utils.update_values("Report", "NETWORK_2", "PASS", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash, uuid_execution)

    print('NETWORK-2 successfully tested.')

    return [verdict, total_matches]
