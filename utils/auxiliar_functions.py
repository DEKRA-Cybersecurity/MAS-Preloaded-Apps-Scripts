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
import json
import glob
import csv


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
            database_utils.insert_values_logging(
                apk_hash, package_name, ct, "CODE-1", "apksigner failed verifying signature", uuid_execution)
            return "Invalid"
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(
            apk_hash, package_name, ct, "CODE-1", "apksigner failed verifying signature", uuid_execution)
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
            database_utils.insert_values_logging(
                apk_hash, package_name, ct, "CODE-2", "grep android:debuggable command failed", uuid_execution)
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

    output = subprocess.check_output(
        cmd, shell=True).decode("utf-8").replace("\n", "")

    if "split" in name:
        package = output + "_" + name
    else:
        package = output

    if package.endswith('<') or package.endswith('>') or package.endswith('/'):
        package = package[:-1]

    return package


def get_hash(wdir):
    '''
    Prints the application's hash - sha256
    '''
    cmd = f"sha256sum {wdir}" + " | awk '{ print $1 }'"
    output = subprocess.check_output(
        cmd, shell=True).decode("utf-8").replace("\n", "")

    return output


def get_suid_from_manifest(wdir):
    cmd_get_suid = f'cat {wdir}/base/AndroidManifest.xml | grep -Po "(?<=android:sharedUserId=)\\"[^\\"]+\\"" | sed \'s/\\"//g\''

    try:
        out_suid = subprocess.check_output(
            cmd_get_suid, shell=True).splitlines()
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
            database_utils.update_values(
                "Report", "NETWORK_1", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Report", "NETWORK_2", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Report", "NETWORK_3", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash, uuid_execution)

    except:
        if internet == "1":
            applies = True
        else:
            database_utils.update_values(
                "Report", "NETWORK_1", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Report", "NETWORK_2", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Report", "NETWORK_3", "NA", "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash, uuid_execution)
            database_utils.update_values(
                "Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash, uuid_execution)

    return applies


def check_app(wdir, apk, apk_hash, package_name, internet, semgrep, uuid_execution):

    # if no content in /sources add in Logging table this error and no scan
    if not (os.path.exists(wdir + '/decompiled/sources') and os.path.isdir(wdir + '/decompiled/sources')):
        print('Application was decompiled and no sources folder was found. Skipping.')
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, package_name, ct, 'Full Application',
                                             'Application was decompiled and no sources folder was found.', uuid_execution)

    else:
        print("Starting scanning process...")
        version_name = get_version_name(wdir)
        script_version = get_script_version()
        database_utils.insert_values_report(
            apk_hash, package_name, version_name, semgrep, script_version, uuid_execution)
        database_utils.insert_values_total_fail_count(apk_hash, uuid_execution)

        with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        # Check if the application has internet permissions or if another application with the same SUID has internet permissions
        applies = check_network_applies(
            wdir, apk_hash, internet, uuid_execution)

        all_params = {'wdir': wdir, 'apk': apk,
                      'apk_hash': apk_hash, 'package_name': package_name, 'uuid_execution': uuid_execution}

        load_and_execute_methods(config['tests'], all_params, applies)

        formula.extract_and_store_permissions(
            apk_hash, package_name, wdir, uuid_execution)


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

    parsed_timestamp = datetime.datetime.strptime(
        timestamp, '%Y-%m-%d %H:%M:%S.%f')

    formatted_timestamp = parsed_timestamp.strftime('%Y%m%d_%H%M%S_%f')[:-3]

    return formatted_timestamp


def load_ADA_json(filepath):
    """Load JSON data from a file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def check_scanned(apk_hash, package_name, wdir, uuid_execution, ada_json_path):

    if os.path.exists(ada_json_path):

        data = load_ADA_json(ada_json_path)
        certificates = data.get("certificates", [])

        version_name = get_version_name(wdir)
        semgrep = use_semgrep()
        script_version = get_script_version()

        for certificate in certificates:
            if certificate.get("packageName") == package_name:
                database_utils.add_analyzed_app(
                    apk_hash, uuid_execution, package_name, version_name, semgrep, script_version)
                formula.extract_and_store_permissions(
                    apk_hash, package_name, wdir, uuid_execution)
                print('APP ' + package_name + ' scanned before.')
                return True
    else:

        return False


def remove_last_backslash(text):
    if text.endswith('\\'):
        return text[:-1]
    return text


def find_zip_image(path):
    search_pattern = os.path.join(path, '*.zip')

    zip_files = glob.glob(search_pattern)

    if len(zip_files) == 1:
        return os.path.basename(zip_files[0])
    elif len(zip_files) == 0:
        raise FileNotFoundError(
            f"No .zip file was found in the directory {path}")
    else:
        raise FileExistsError(
            f"Several .zip files were found in the directory {path}")


def get_formula_csv_path(execution_folder):

    if not os.path.exists(execution_folder):
        raise FileNotFoundError(f"Path: '{execution_folder}' does not exists.")

    csv_file_path = None
    for file_name in os.listdir(execution_folder):
        if "Formula" in file_name and file_name.endswith('.csv'):
            csv_file_path = os.path.join(execution_folder, file_name)
            break

    if csv_file_path is None:
        raise FileNotFoundError(
            f"Formula CSV file was not find in {execution_folder} folder.")

    return csv_file_path


def get_full_file_path(path, file):
    for filename in os.listdir(path):
        if file in filename:
            return os.path.join(path, filename)
    return None

def get_full_folder_path(path, id_execution):
    for foldername in os.listdir(path):
        full_path = os.path.join(path, foldername)
        if os.path.isdir(full_path) and id_execution in foldername:
            return foldername
    return None

def insert_findings(id_execution, path):
    file_path = get_full_file_path(path, 'Findings')

    if file_path:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            next(csv_reader)

            for row in csv_reader:
                if row:
                    hash = row[0]
                    app_name = row[1]
                    category = row[2]
                    check_id = row[3]
                    finding_path = row[4]
                    line = row[5]

                    finding_data = (hash, app_name, category,
                                    check_id, finding_path, line, str(id_execution))

                    database_utils.insert_new_finding(finding_data)
    else:
        print('CSV file with list of findings was not found.')


def insert_permissions(id_execution, path):
    file_path = get_full_file_path(path, 'Permissions')

    if file_path:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            next(csv_reader)

            for row in csv_reader:
                if row:
                    hash = row[0]
                    app_name = row[1]
                    permissions = row[2]

                    database_utils.insert_values_permissions(
                        hash, app_name, permissions, str(id_execution))
    else:
        print('CSV file with list of permissions was not found.')


def insert_report(id_execution, path):
    file_path = get_full_file_path(path, 'Report')

    if file_path:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            next(csv_reader)

            for row in csv_reader:
                if row:
                    hash = row[0]
                    app_name = row[1]
                    version_name = row[2]
                    semgrep = row[3]
                    script_version = row[4]
                    code_1 = row[5]
                    code_2 = row[6]
                    crypto_1 = row[7]
                    crypto_3 = row[8]
                    network_1 = row[9]
                    network_2 = row[10]
                    network_3 = row[11]
                    platform_2 = row[12]
                    platform_3 = row[13]
                    storage_2 = row[14]

                    report_data = (hash, str(id_execution), app_name, version_name, semgrep, script_version, code_1,
                                   code_2, crypto_1, crypto_3, network_1, network_2, network_3, platform_2, platform_3, storage_2)

                    database_utils.insert_new_report(report_data)
    else:
        print('CSV file with list of report was not found.')


def insert_total_fail_counts(id_execution, path):
    file_path = get_full_file_path(path, 'Total_Fail_Counts')

    if file_path:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            next(csv_reader)

            for row in csv_reader:
                if row:
                    hash = row[0]
                    code_1 = row[1]
                    code_2 = row[2]
                    crypto_1 = row[3]
                    crypto_3 = row[4]
                    network_1 = row[5]
                    network_2 = row[6]
                    network_3 = row[7]
                    platform_2 = row[8]
                    platform_3 = row[9]
                    storage_2 = row[10]

                    tfc_data = (hash, str(id_execution), code_1, code_2, crypto_1, crypto_3,
                                network_1, network_2, network_3, platform_2, platform_3, storage_2)

                    database_utils.insert_new_total_fail_counts(tfc_data)
    else:
        print('CSV file with list of total fail counts was not found.')


def insert_values(id_execution, path):

    actual_date = datetime.datetime.now()
    formated_date = actual_date.strftime('%Y-%m-%d %H:%M:%S.%f')

    database_utils.insert_new_execution(str(id_execution), formated_date)

    insert_findings(id_execution, path)
    insert_permissions(id_execution, path)
    insert_report(id_execution, path)
    insert_total_fail_counts(id_execution, path)
