import subprocess
import datetime
from settings import PATH_APKSIGNER
import db.database_utils as database_utils
import base64
import yaml
import importlib
import utils.formula as formula
import xml.etree.ElementTree as ET
import os
import re
import requests

def check_signature(wdir, apk, apk_hash, package_name, uuid_execution):
    '''
    Returns output of apksigner to verify the signature.
    '''
    try:
        cmd = f"{PATH_APKSIGNER} verify -verbose {wdir}/{apk}"
        output = [i.decode("utf-8")
                  for i in subprocess.check_output(cmd, shell=True, timeout=300).splitlines()]
        return output
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return "Invalid"
            pass 
        else:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, package_name, ct, "CODE-1", "apksigner failed verifying signature", uuid_execution)
            return "Invalid"
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, "CODE-1", "apksigner failed verifying signature", uuid_execution)
        return "Invalid"

def check_debuggable(wdir, apk_hash, package_name, uuid_execution):
    '''
    Check if the application uses android:debuggable="true" in AndroidManifest.xml file
    '''
    cmd = f"grep -n --exclude='*.dex' -iE 'android:debuggable=\"true\"' {wdir}/base/AndroidManifest.xml"
    try:
        output = subprocess.check_output(cmd, shell=True).splitlines()
    except subprocess.CalledProcessError as e:
        ct = datetime.datetime.now()
        if e.returncode == 2:
            database_utils.insert_values_logging(apk_hash, package_name, ct, "CODE-2", "grep android:debuggable command failed", uuid_execution)
            output = "Error"
        else:
            output = "No relevant results"

    return output

def check_package_name(wdir, name):
    '''
    Prints the package name.
    '''
    # awk -F 'package=' '{print $2}' | awk -F' ' '{print $1}' | sed s/\"//g
    grep = "YXdrIC1GICdwYWNrYWdlPScgJ3twcmludCAkMn0nIHwgYXdrIC1GJyAnICd7cHJpbnQgJDF9JyB8IHNlZCBzL1wiLy9n"
    d_grep = base64.b64decode(grep).decode("utf-8")
    cmd = f"cat {wdir}/base/AndroidManifest.xml | {d_grep}"

    output = subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n", "")

    if "split" in name:
        package = output + "_" + name
    else:
        package = output

    if package.endswith('<') or package.endswith('>') or package.endswith('/'):
        package =  package[:-1] 

    return package

def check_hash_apk(wdir):
    '''
    Prints the application's hash - sha256
    '''
    cmd = f"sha256sum {wdir}/base.apk" + " | awk '{ print $1 }'"
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n", "")

    return output

def get_suid_from_manifest(wdir):
    cmd_get_suid = f'cat {wdir}/base/AndroidManifest.xml | grep -Po "(?<=android:sharedUserId=)\\"[^\\"]+\\"" | sed \'s/\\"//g\''

    try:
        out_suid = subprocess.check_output(cmd_get_suid, shell=True).splitlines()
        out_suid_string = out_suid[0].decode()
    except:
        out_suid_string = ""  # No tiene SUID

    return out_suid_string

def check_network_applies(wdir, apk_hash, internet, uuid_execution):

    out_suid_string = get_suid_from_manifest(wdir)
    applies = False

    try:
        file = open(out_suid_string, 'r')

        content = file.read().splitlines()[0]

        if content == "1":
            applies = True
        elif content == "0":
            database_utils.update_values("Report", "NETWORK_1", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Report", "NETWORK_2", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Report", "NETWORK_3", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash, uuid_execution)

    except:
        if internet == "1":
            applies = True
        else:
            database_utils.update_values("Report", "NETWORK_1", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Report", "NETWORK_2", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Report", "NETWORK_3", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash, uuid_execution)

    return applies

def check_app(wdir, apk, apk_hash, package_name, internet, semgrep, uuid_execution):

    # if no content in /sources add in Logging table this error and no scan
    if not (os.path.exists(wdir + '/decompiled/sources') and os.path.isdir(wdir + '/decompiled/sources')):
        print('Application was decompiled and no sources folder was found. Skipping.')
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, 'Full Application', 'Application was decompiled and no sources folder was found.', uuid_execution)

    else:
        print("Starting scanning process...")
        version_name = get_version_name(wdir)
        script_version = get_script_version()
        database_utils.insert_values_report(apk_hash, package_name, version_name, semgrep, script_version, uuid_execution)
        database_utils.insert_values_total_fail_count(apk_hash, uuid_execution)

        with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        # Check if the application has internet permissions or if another application with the same SUID has internet permissions
        applies = check_network_applies(wdir, apk_hash, internet, uuid_execution)

        all_params = {'wdir': wdir, 'apk': apk,
                    'apk_hash': apk_hash, 'package_name': package_name, 'uuid_execution': uuid_execution}

        load_and_execute_methods(config['tests'], all_params, applies)

        formula.extract_and_store_permissions(apk_hash, package_name, wdir, uuid_execution)

def load_and_execute_methods(config, all_params, applies):
    for category, tests in config.items():
        for test in tests:
            module_name = f"tests.{category}.{test}"
            try:
                if category != 'network' or (category == 'network' and applies):
                    module = importlib.import_module(module_name)
                    method_func = getattr(module, 'check')
                    method_func(**all_params)
            except ImportError as e:
                print(f"Failed to import module {module_name}: {e}")
            except AttributeError:
                print(f"Method check not found in {module_name}")

def use_semgrep():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    use = bool(config.get("semgrep", {}))

    return use

def get_script_version():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    version = config.get("version", {})

    return str(version)

def export_csv():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    export_csv = bool(config.get("export_csv", {}))

    return export_csv

def get_version_name(wdir):
    try:
        with open(os.path.join(wdir + '/base/AndroidManifest.xml'), 'r') as file:
            content = file.read()

            match = re.search(r'android:versionName\s*=\s*"([^"]+)"', content)

            if match:
                return match.group(1)
            else:
                return ''

    except Exception as e:
        return ''
    
def parse_timestamp(timestamp):
    
    parsed_timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

    formatted_timestamp = parsed_timestamp.strftime('%Y%m%d_%H%M%S_%f')[:-3]

    return formatted_timestamp
    
def check_scanned(apk_hash, package_name, wdir, uuid_execution):

    certs = requests.get("https://appdefense-dot-devsite-v2-prod-3p.appspot.com/directory/data/certs.json").json()

    version_name = get_version_name(wdir)
    semgrep = use_semgrep()
    script_version = get_script_version()

    for cert in certs["certificates"]:
        if 'packageName' in cert and cert['packageName'] == package_name:
            database_utils.add_analyzed_app(apk_hash, uuid_execution, package_name, version_name, semgrep, script_version)
            formula.extract_and_store_permissions(apk_hash, package_name, wdir, uuid_execution)
            print('APP ' + package_name + ' scanned before.')
            return True
        
    return False

def remove_last_backslash(text):
    if text.endswith('\\'):
        return text[:-1]
    return text
