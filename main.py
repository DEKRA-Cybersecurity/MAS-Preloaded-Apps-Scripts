#!/usr/bin/python

import sys
import os
from utils.auxiliar_functions import check_package_name, check_hash_apk, check_app


'''
Automated mobile applications test cases evaluator

See README.txt for execution instructions

'''

def main():

    check_app(wdir, apk, apk_hash, package_name, internet)

if __name__ == "__main__":

    wdir = os.path.join(sys.argv[1])
    internet = sys.argv[2]
    package_name = check_package_name(wdir, os.path.basename(wdir))
    apk = 'base.apk'
    apk_hash = check_hash_apk(wdir)

    sys.exit(main())