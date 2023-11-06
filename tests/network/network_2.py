import subprocess
import datetime
import db.database_utils as database_utils
from settings import PATH_TESTSSL
from utils.auxiliar_functions import get_suid_from_manifest

def check(wdir, apk_hash):
    '''
        Check for potentially vulnerable TLS configurations.
        If a match is found, INCONCLUSIVE is set, could be a potential FAIL
        This case creates a report that shall be reviewed manually to inspect for a verdict in the Test Case

        Future work: check with a whitelist of URLs if they are considered PASS even if they allow TLS1 or TLS1.1 according to ciphersuites.
    '''
    total_matches = 0
    is_inconclusive = False
    grep_filter = ["\"((SSLv2).*(deprecated))|((SSLv3).*(deprecated))|((TLS 1).*(deprecated))|((TLS 1.1).*(deprecated))\"",
                   "\"((TLSv1:)|(TLSv1.1:)).*(-DES-[A-Z0-9]+)\""]
    with open(wdir+'/_filtered_net2.txt') as all_urls:

        for url in all_urls:
            url_no_breakline = url.rstrip("\n")
            cmd = f'echo no | {PATH_TESTSSL} -P {url_no_breakline} 2>/dev/null | grep -E {grep_filter[1]} | wc -l'

            results = database_utils.get_values(
                "TestSSL_URLS", "URL", url_no_breakline)
            if not results:
                try:
                    output = subprocess.check_output(
                        cmd, shell=True).splitlines()
                    if int(output[0]) > 0:
                        total_matches += 1
                except:
                    ct = datetime.datetime.now()
                    database_utils.insert_values_logging(
                        apk_hash, ct, "NETWORK-2", "Command failed.")
                    pass  # No output

                if total_matches > 0:
                    is_inconclusive = True
                    database_utils.insert_values_testsslURLs(
                        url_no_breakline, "Needs Review")
                else:
                    database_utils.insert_values_testsslURLs(
                        url_no_breakline, "Pass")

            else:
                if results[0][1] == "INCONCLUSIVE":
                    is_inconclusive = True
                elif results[0][1] == "PASS":
                    is_inconclusive = False

            total_matches = 0

    if is_inconclusive:
        database_utils.update_values(
            "Report", "NETWORK_2", "Needs Review", "HASH", apk_hash)
        database_utils.update_values(
            "Total_Fail_Counts", "NETWORK_2", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values(
            "Report", "NETWORK_2", "Pass", "HASH", apk_hash)
        database_utils.update_values(
            "Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash)

    print('NETWORK-2 successfully tested.')
