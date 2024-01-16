from tests.network.network_1 import check

def test_check():

    data = {'wdir': './unit_tests/reference_apk/Bluetooth', 'apk': 'base.apk', 'apk_hash': '56c85552ff7034997435761e9b0bd2ef05ea8e2d686423b13a005032c9237f73', 'package_name': 'com.android.bluetooth'}

    assert check(**data) == 'PASS'