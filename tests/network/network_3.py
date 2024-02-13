import subprocess
import datetime
import db.database_utils as database_utils
from utils.auxiliar_functions import get_suid_from_manifest

def check(wdir, apk, apk_hash, package_name):
    verdict = 'FAIL'
    net_config = False
    low_target_Sdk = False
    total_matches = 0
    verifier_check = "\"(import java(x)?\\.(.*)HostnameVerifier;)\"" 
    
    cmd =f"cat {wdir}/base/AndroidManifest.xml |  egrep -iE 'android:networkSecurityConfig' | wc -l"
    try:
        output = subprocess.check_output(cmd, shell=True).strip()
        if int(output) > 0:
            net_config = True
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            net_config = False
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(
                apk_hash, ct, "NETWORK-3", "Network security config file grep error")
    except:
        net_config = False
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(
            apk_hash, ct, "NETWORK-3", "Network security config file grep error")
        pass

    cmd_get_target_sdk = f'cat {wdir}/base/AndroidManifest.xml | grep -Po \"(?<=android:targetSdkVersion=)\\"[^\\"]+\\"\" | sed \'s/\"//g\''
    try:
        output = subprocess.check_output(cmd_get_target_sdk, shell=True).splitlines()
        if int(int(output[0])) < 24:
            low_target_Sdk = True
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            low_target_Sdk = False
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "NETWORK-3", "Target sdk grep error")
    except:
        low_target_Sdk = False
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "NETWORK-3", "Target sdk grep error")

    cmd_check_hostnameverifier = f"grep -rnwz --exclude='*.dex' -E {verifier_check} {wdir}/decompiled/sources | wc -l"
    try:
        output = subprocess.check_output(cmd_check_hostnameverifier, shell=True).splitlines()
        if int(output[0]) > 0:
            total_matches += 1 
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(
                apk_hash, ct, "NETWORK-3", "hostname verifier functions grep error or not found")
            pass  # No output
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(
            apk_hash, ct, "NETWORK-3", "hostname verifier functions grep error or not found")
        pass  # No output

    with open(wdir+'/report_'+package_name+'.txt', 'a+') as f:
        if net_config == True and total_matches == 0:
            database_utils.update_values("Report", "NETWORK_3", "Needs Review", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 1, "HASH", apk_hash)
            verdict = 'Needs Review'
        elif net_config == False and low_target_Sdk == True and total_matches == 0:
            database_utils.update_values("Report", "NETWORK_3", "FAIL", "HASH", apk_hash)
            database_utils.insert_new_dekra_finding(apk_hash, package_name, "NETWORK", "NETWORK-3", wdir + "/base/AndroidManifest.xml", '-')                 
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 1, "HASH", apk_hash)
        elif net_config == False and low_target_Sdk == False or total_matches > 0:
            database_utils.update_values("Report", "NETWORK_3", "PASS", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash)
            verdict = 'PASS'
        else:
            database_utils.update_values("Report", "NETWORK_3", "Needs Review", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash)
            
    print('NETWORK-3 successfully tested.')

    return verdict