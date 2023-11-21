import subprocess
import datetime
import db.database_utils as database_utils 

def check(wdir, apk, apk_hash, package_name):
    '''
    Checks for WRITE_EXTERNAL_STORAGE in AndroidManifest.xml file.

    If it is not found, it is a PASS
    '''
    output_write_external = 0
    cmd = f'cat {wdir}/base/AndroidManifest.xml | grep WRITE_EXTERNAL_STORAGE'

    try:
        out = subprocess.check_output(cmd, shell=True).splitlines()
        output_write_external += 1   
    except subprocess.CalledProcessError as e:
        ct = datetime.datetime.now()
        if e.returncode == 1: #permission not found
            pass
        else:
            database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", "grep for WRITE_EXTERNAL_STORAGE permission failed. File not found")
            pass
    
    total_matches = 0
    verdict = 'FAIL'

    if output_write_external >= 1:

        storage_functions = ["getExternalStorageDirectory", "getExternalFilesDir"]

        for i in storage_functions:
            cmd = f"grep -rlnwz -E {i} {wdir}/decompiled | wc -l"
            try:
                output = subprocess.check_output(cmd, shell=True).splitlines()
                if int(output[0]) > 0:
                    total_matches += int(output[0]) 
            except:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", f"grep command failed for {i}")
                pass #No output
                
        if total_matches > 0:
            database_utils.update_values("Report", "STORAGE_2", "Fail", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)

        else:
            database_utils.update_values("Report", "STORAGE_2", "Pass", "HASH", apk_hash) #Manual check is advised, no matches
            database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)
            verdict = 'PASS'

    elif output_write_external == 0:
        database_utils.update_values("Report", "STORAGE_2", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)
        verdict = 'PASS'

    print('STORAGE-2 successfully tested.')

    return verdict