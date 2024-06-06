#!/usr/bin/python

import sys
import os
from utils.auxiliar_functions import check_package_name, check_hash_apk, check_app, use_semgrep, check_scanned
from utils.semgrep_functions import semgrep_scan

'''
Automated mobile applications test cases evaluator

See README.txt for execution instructions

'''

def main():

    scanned = check_scanned(apk_hash, package_name, wdir, uuid_execution, ada_json_path)

    if not scanned and semgrep:
            semgrep_scan(wdir, apk_hash, package_name, uuid_execution)
    elif not scanned and not semgrep:
            check_app(wdir, apk, apk_hash, package_name, internet, semgrep, uuid_execution)
    else:
        print('The results of the ' + package_name + ' app were obtained from App Defence Aliance.')
        

if __name__ == "__main__":

    wdir = os.path.join(sys.argv[1])
    internet = sys.argv[2]
    uuid_execution = sys.argv[3]
    ada_json_path = sys.argv[4]
    package_name = check_package_name(wdir, os.path.basename(wdir))
    apk = 'base.apk'
    apk_hash = check_hash_apk(wdir)
    semgrep = use_semgrep()

    print('Scanning app: ' + package_name)

    sys.exit(main())