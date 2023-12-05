import os

# -------------------------
#      PATH SETTINGS
# -------------------------

PATH_APKTOOL = os.getenv('PATH_APKTOOL', './tools/apktool.jar')
PATH_APKSIGNER = os.getenv('PATH_APKSIGNER', './tools/apksigner')
PATH_JADX = os.getenv('PATH_JADX', './tools/jadx/bin/jadx')
PATH_TESTSSL = os.getenv('PATH_TESTSSL', './tools/testssl2')
DB_USER_MASA = os.getenv('DB_USER_MASA', 'masa_script')
DB_PASSWORD_MASA = os.getenv('DB_PASSWORD_MASA', 'MASA123')
RULES_SEMGREP_PATH= os.getenv('RULES_SEMGREP_PATH', './semgrep-rules/rules')