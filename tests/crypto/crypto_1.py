import subprocess
import datetime
import db.database_utils as database_utils

def check(wdir, apk, apk_hash, package_name, uuid_execution):

    '''
        Hardcoded Byte arrays, b64 str or final Strings in files where crypto lib are imported
        Key generation with hardcoded parameters
        Triple backward slash to get escaped \"
        Output is always multiline, so len of output is not necessarily required, only a match is enough.
        However, if other regular expressions are imported, it may be useful in the future 
    '''
    verdict = 'FAIL'
    total_matches = 0
    regex_1 = "\"import java(x)?\.(security|crypto).*;(\\n|.)*((final String [a-zA-Z0-9]+[ ]*\\=)|(==\\\")|(byte\\[\\] [a-zA-Z0-9]* = [{]{1}[ ]?[0-9]+)|(SecretKeySpec\\(((\\{[0-9]+)|(\\\"[a-zA-Z0-9]+\\\"))))\""
    regex_2 = "\"Lcom\/jiolib\/libclasses\/utils\/AesUtil\""

    cmd = f"grep -rlnwzs --exclude='*.dex' -E {regex_1} {wdir}/decompiled/sources"
    try:
        output = subprocess.check_output(cmd, shell=True).splitlines()
        if len(output) > 0:
            total_matches += len(output)
            for match in output:
                match_file = match.decode()
                database_utils.insert_new_finding([apk_hash, package_name, "CRYPTO", "CRYPTO-1", match_file, '-', uuid_execution])             
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "CRYPTO-1", f"grep command failed due to {wdir}/decompiled/sources does not exists", uuid_execution)
            pass #No output
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, "CRYPTO-1", f"grep command failed for {regex_1}", uuid_execution)
        pass #No output

    cmd = f"grep -rlnws --exclude='*.dex' -E {regex_2} {wdir}/decompiled/sources"
    try:
        output = subprocess.check_output(cmd, shell=True, timeout=300).splitlines()
        if len(output) > 0:
            total_matches += len(output)
            for match in output:
                match_file = match.decode().split(":")[0]
                match_line = match.decode().split(":")[1] 
                database_utils.insert_new_finding([apk_hash, package_name, "CRYPTO", "CRYPTO-1", match_file, match_line, uuid_execution])             
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "CRYPTO-1", f"grep command failed due to {wdir}/decompiled/sources does not exists", uuid_execution)
            pass #No output
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, "CRYPTO-1", f"grep command failed for {regex_2}", uuid_execution)
        pass #No output
            
    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_1", "FAIL", "HASH", apk_hash, uuid_execution)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_1", total_matches, "HASH", apk_hash, uuid_execution)
    else:
        verdict = 'PASS'
        database_utils.update_values("Report", "CRYPTO_1", "PASS", "HASH", apk_hash, uuid_execution) #Manual check is advised, no matches
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_1", total_matches, "HASH", apk_hash, uuid_execution)     

    print('CRYPTO-1 successfully tested.')

    return [verdict, total_matches]
