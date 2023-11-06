import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk_hash):
    '''
    The primary objective is to search for potential SQL injection in queries.
    A main regex to search for these queries is applied. 
    
    E.g:
    "SELECT Column FROM Table WHERE id = " + input_variable + " ... ;"

    May suggest that an user could inject malicious SQL code to cause an injection. 

    If a match with these queries is registered, it may conclude in an INCONCLUSIVE.


    Dynamic analysis: Add drozer module to query and extract potential injections in content providers.
    Drozer can be launched in cmdline.

    docker run fsecurelabs/drozer /bin/bash -c "drozer console connect --server 192.168.3.14 -c 'run scanner.provider.injection -a com.android.chrome'";
    '''
    total_matches = 0
    vuln_parameters = ["\"\\\"[ ]*(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})[a-zA-Z0-9\\ \\*_\\-]+(\=)(\\ |\\\")[ ]?\\\+\"", "\"(shouldOverrideUrlLoading\\(.*\\{)[\\n\\s\\t]*return false;(\\n|[\\s\\t])\\}\""]
    #cmd_webview = f'grep -rnwz -E {wdir}/decompiled | wc -l'

    for i in vuln_parameters:
        cmd = f"grep -rlnwz -E {i} {wdir}/decompiled | wc -l" #cmd = f"grep -rnwz -E {vuln_parameters[0]} {wdir}/decompiled | wc -l"
  
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if int(output[0]) > 0:
                total_matches = int(output[0]) 
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "PLATFORM-2", "grep failed  for {i}")
            pass #No output
            
    if total_matches > 0:
        database_utils.update_values("Report", "PLATFORM_2", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_2", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "PLATFORM_2", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_2", 0, "HASH", apk_hash)

    print('PLATFORM-2 successfully tested.')
