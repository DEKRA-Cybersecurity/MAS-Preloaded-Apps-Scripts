Imports for python script:

Profile
os
base64
time
xml.etree.ElementTree
subprocess
sys
pandas
openpyxl
mysql.connector

Tools required:

mysql
nm
apktool
jadx
checksec
apksigner
adb
libscout
testssl tool provided in a script testssl2

testssl2 tool is set to be stored in this directory: ~/Documents/Tools/testssl2. However, this path can be modified if needed in the top side of MASA_automator.py script.


NVD Api key must be placed in statics.py file when applying CODE-5 review, and the appropriate column must be added.
LibScout path may be needed to be altered in MASA_automator.py file:

path_libscout = "~/Documents/Tools/LibScout/build/libs/LibScout.jar"
path_android_jar = "~/Android/Sdk/platforms/android-31/android.jar"
path_libscout_config = "~/Documents/Tools/LibScout/config/LibScout.toml"

Script setup:

All applications need to be distributed in folders as shown below:

root_dir
        |__MASA_automator_script.py - python script
        |__automate_MASA_automator.sh - bash script
        |__config.py - Python script to config database the first time is used in a machine.
        |__database_utils.py - Python script that includes database utility functions.
        .
        .        
        .
        |
        |
        |__App_1
        |       |
        |       |__base.apk
        |__App_2
        |       |
        |       |__base.apk
        |
        |
        .
        .
        .
        |__App_n
                |
                |__base.apk


Before anything is executed, MySQL database must have an username called "mysqluser" with password "mysqlpassword"
To setup the database, the script config.py must be executed first, in order to generate all tables.

When automate_MASA_automator is executed, it extracts (apktool) and decompiles (jadx) the base.apk file
Then executes the python script, generating the report in the MySQL database.

When an application is analyzed, the wrapper script deletes any base/decompiled folder to free disk space.
Reports will be stored in MySQL database.

To extract the reports from the database:

python3 Collect_data.py

Sometimes, the first row of data will be empty for some test cases, and no app name will be shown. This row can be ignored/deleted as it is created from an empty apk file

To clear database entries for a new device: python3 cleardb.py

Manual review is advised.
