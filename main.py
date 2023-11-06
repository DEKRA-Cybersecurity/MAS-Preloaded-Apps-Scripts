#!/usr/bin/python

import sys
import db.database_utils
import os
import utils.formula as formula
from utils.auxiliar_functions import check_network_applies

from tests.code import code_1, code_2
from tests.crypto import crypto_1, crypto_3
from tests.storage import storage_2
from tests.platform import platform_2, platform_3
from tests.network import network_1, network_2, network_3

from utils.auxiliar_functions import check_package_name, check_hash_apk

'''
Automated mobile applications test cases evaluator

See README.txt for execution instructions

'''

def main():

    print("Starting scanning process...")
    db.database_utils.insert_values_report(apk_hash, package_name)
    db.database_utils.insert_values_total_fail_count(apk_hash)

    # MSTG-CODE-1
    code_1.check(wdir, apk, apk_hash)

    # MSTG-CODE-2
    code_2.check(wdir, apk, apk_hash)

    # MSTG-CRYPTO-1
    crypto_1.check(wdir, apk_hash)

    # MSTG-CRYPTO-3
    crypto_3.check(wdir, apk_hash)

    # MSTG-STORAGE-2
    storage_2.check(wdir, apk_hash)

    # MSTG-PLATFORM-2
    platform_2.check(wdir, apk_hash)

    # MSTG-PLATFORM-3
    platform_3.check(wdir, apk_hash)

    # Check if the application has internet permissions or if another application with the same SUID has internet permissions
    applies = check_network_applies(wdir, apk_hash, internet)

    # The application has internet permissions or another application with the same SUID has internet permissions.
    if applies:

        # MSTG-NETWORK-1
        network_1.check(wdir, apk_hash)

        # MSTG-NETWORK-2
        network_2.check(wdir, apk_hash)

        # MSTG-NETWORK-3
        network_3.check(wdir, package_name, apk_hash)

    formula.extract_and_store_permissions(apk_hash, package_name, wdir+"/base/AndroidManifest.xml")

if __name__ == '__main__':
    wdir = os.path.join(sys.argv[1])
    internet = sys.argv[2]
    package_name = check_package_name(wdir, os.path.basename(wdir))
    apk = 'base.apk'
    apk_hash = check_hash_apk(wdir)

    sys.exit(main())

