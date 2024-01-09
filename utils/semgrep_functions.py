import subprocess
import os
import json
import openpyxl
import time
from openpyxl import Workbook
from settings import RULES_SEMGREP_PATH
import re
import db.database_utils as database_utils
from utils.auxiliar_functions import get_version_name, dekra_script_version

def scan_with_semgrep(target_path, rules_path):
    final_path = os.path.join(target_path, 'decompiled/sources/')
    start_time = time.time()
    cmd = ["semgrep", "--config", rules_path, "--json", final_path, "--no-git-ignore"]
    findings_list = []
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        findings = json.loads(result.stdout)
        
        for finding in findings.get("results", []):
            check_id = finding.get("check_id", "N/A")
            path = finding.get("path", "N/A")
            start_line = finding.get("start", {}).get("line", "N/A")
            findings_list.append(finding)

    except subprocess.CalledProcessError as e:
        print(f"Semgrep encountered an error: {e}")
    except Exception as e:
        print(f"Unexpected error processing {rules_path}. Details: {e}")
        
    elapsed_time = (time.time() - start_time) / 60  
    return findings_list, elapsed_time

def extract_tc(tc_text):

    pattern = r'\.MSTG-(.*?-\d+)'

    match = re.search(pattern, tc_text)

    tc = match.group(1)
    return tc

def write_to_database(app_results, apk_hash, package_name, version_name, script_version):
    
    res_app = {
        "HASH" : apk_hash, 
        "APP_NAME" : package_name, 
        "VERSION_NAME" : version_name,
        "SEMGREP" : True,
        "SCRIPT_VERSION" : script_version,
        "CODE-1" : "N/A", 
        "CODE-2": "PASS", 
        "CRYPTO-1" : "PASS", 
        "CRYPTO-3" : "N/A",
        "NETWORK-1" : "N/A", 
        "NETWORK-2" : "PASS", 
        "NETWORK-3" : "N/A", 
        "PLATFORM-2" : "N/A", 
        "PLATFORM-3" : "PASS", 
        "STORAGE-2" : "PASS",
        
    }

    for app_name, category_results in app_results.items():
        for category, (findings, scan_time) in category_results.items():
            for finding in findings:
                check_id = finding.get("check_id", "N/A")
                path = finding.get("path", "N/A")
                start_line = finding.get("start", {}).get("line", "N/A")
                res_app[extract_tc(check_id)] = "FAIL"
                database_utils.insert_new_finding([apk_hash, package_name, category, check_id, path, start_line])

    database_utils.insert_new_report(list(res_app.values()))


def analyze_app(app_dir):
    app_name = os.path.basename(app_dir)
    category_results = {}

    for category in os.listdir(RULES_SEMGREP_PATH):
        category_path = os.path.join(RULES_SEMGREP_PATH, category)
        
        if os.path.isdir(category_path):
            print(f"Scanning OWASP MASTG category: {category} for {app_name}")
            start_time = time.time()

            all_findings = []
            for testcase in os.listdir(category_path):
                if testcase.endswith(".yaml"):
                    testcase_path = os.path.join(category_path, testcase)
                    findings, _ = scan_with_semgrep(app_dir, testcase_path)
                    all_findings.extend(findings)

            scan_time = (time.time() - start_time) / 60  # Convert to minutes
            category_results[category] = (all_findings, scan_time)

    return app_name, category_results

def semgrep_scan(wdir, apk_hash, package_name):

    app_results = {}

    if os.path.isdir(wdir):
        app_name, category_results = analyze_app(wdir)
        app_results[app_name] = category_results

    if app_results:
        version_name = get_version_name(wdir)
        script_version = dekra_script_version()
        write_to_database(app_results, apk_hash, package_name, version_name, script_version)
    else:
        print("No findings detected across all apps.")