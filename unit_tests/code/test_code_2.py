from tests.code.code_2 import check

def test_check():

    data = {'wdir': './unit_tests/reference_apk/Calendar', 'apk': 'base.apk', 'apk_hash': '153348855f3b29b026063fb4fc3dd8d225498048b0608c2442434a5bc81e62ee', 'package_name': 'com.android.providers.calendar'}

    assert check(**data) == 'PASS'