import subprocess
import datetime
import db.database_utils as database_utils 

def check(wdir, apk, apk_hash, package_name):
    '''
    Checks for WRITE_EXTERNAL_STORAGE in AndroidManifest.xml file.

    If it is not found, it is a PASS
    '''
    output_write_external = 0
    cmd = f"grep -n -iE WRITE_EXTERNAL_STORAGE {wdir}/base/AndroidManifest.xml"

    try:
        output = subprocess.check_output(cmd, shell=True).splitlines()
        if output:
            output_write_external += 1   
            match_line = output[0].decode().strip().split(':', 1)[0]
            database_utils.insert_new_dekra_finding(apk_hash, package_name, "STORAGE", "STORAGE-2", wdir + "/base/AndroidManifest.xml", match_line)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", "grep for WRITE_EXTERNAL_STORAGE permission failed. File not found")
            pass
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", "grep for WRITE_EXTERNAL_STORAGE permission failed. File not found")
        pass #No output
    
    total_matches = 0
    verdict = 'FAIL'

    if output_write_external >= 1:

        storage_functions = ["getExternalStorageDirectory", "getExternalFilesDir"]

        for i in storage_functions:
            cmd = f"grep -rnw -E {i} {wdir}/decompiled"
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
                                database_utils.insert_new_dekra_finding(apk_hash, package_name, "STORAGE", "STORAGE-2", match_file, match_line)             
                            else:             
                                set_matches.add(match_str)
                                database_utils.insert_new_dekra_finding(apk_hash, package_name, "STORAGE", "STORAGE-2", match_str, '-')
                        except:
                            print('[ERROR] It was not possible to get match_file or match_line')
                total_matches += len(set_matches)
            except subprocess.CalledProcessError as e:
                if e.returncode == 1:
                    pass 
                else:
                    ct = datetime.datetime.now()
                    database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", f"grep command failed for {i}")
                    pass
            except:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", f"grep command failed for {i}")
                pass #No output
                
        if total_matches > 0:
            database_utils.update_values("Report", "STORAGE_2", "FAIL", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)

        else:
            database_utils.update_values("Report", "STORAGE_2", "PASS", "HASH", apk_hash) #Manual check is advised, no matches
            database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)
            verdict = 'PASS'

    elif output_write_external == 0:
        database_utils.update_values("Report", "STORAGE_2", "PASS", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)
        verdict = 'PASS'

    print('STORAGE-2 successfully tested.')

    return verdict