import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name, uuid_execution):
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
    verdict = 'FAIL'
    total_matches = 0
    regex_1 = "\"\\\"[ ]*(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})[ ]+[a-zA-Z0-9\\ \\*_\\-\\=]+(\\ |\\\")[ ]?\\+[ ]*[a-zA-Z0-9\\ \\*_\\-]+\""
    regex_2 = "\"shouldOverrideUrlLoading\\(.*\\)[ ]*{[\\n\\s\\t]*(return false;)\""
    #cmd_webview = f'grep -rnwz -E {wdir}/decompiled | wc -l'

    cmd = f"grep -rnws --exclude='*.dex' -E {regex_1} {wdir}/decompiled/sources"
    try:
        output = subprocess.check_output(cmd, shell=True, timeout=300).splitlines()
        if len(output) > 0:
            total_matches += len(output)
            for match in output:
                match_str = match.decode()
                try:
                    if '.java' in match_str:
                        match_file = match_str.split(":")[0]
                        match_line = match_str.split(":")[1] 
                        database_utils.insert_new_finding([apk_hash, package_name, "PLATFORM", "PLATFORM-2", match_file, match_line, uuid_execution])
                    else:
                        database_utils.insert_new_finding([apk_hash, package_name, "PLATFORM", "PLATFORM-2", match_str, '-', uuid_execution])
                except:
                    print('[ERROR] It was not possible to get match_file or match_line')
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "PLATFORM-2", f"grep command failed due to {wdir}/decompiled/sources does not exists", uuid_execution)
            pass
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, "PLATFORM-2", f"grep failed  for {regex_1}", uuid_execution)
        pass #No output

    cmd = f"grep -rlnwzs --exclude='*.dex' -P {regex_2} {wdir}/decompiled/sources"
    try:
        output = subprocess.check_output(cmd, shell=True).splitlines()
        if len(output) > 0:
            total_matches += len(output)
            for match in output:
                match_str = match.decode()
                try:
                   database_utils.insert_new_finding([apk_hash, package_name, "PLATFORM", "PLATFORM-2", match_str, '-', uuid_execution])
                except:
                    print('[ERROR] It was not possible to get match_str')
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "PLATFORM-2", f"grep command failed due to {wdir}/decompiled/sources does not exists", uuid_execution)
            pass
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, "PLATFORM-2", f"grep failed  for {regex_2}", uuid_execution)
        pass #No output
            
    if total_matches > 0:
        database_utils.update_values("Report", "PLATFORM_2", "FAIL", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_2", total_matches, "HASH", apk_hash, uuid_execution)
    else:
        database_utils.update_values("Report", "PLATFORM_2", "PASS", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_2", total_matches, "HASH", apk_hash, uuid_execution)
        verdict = 'PASS'

    print('PLATFORM-2 successfully tested.')

    return [verdict, total_matches]
