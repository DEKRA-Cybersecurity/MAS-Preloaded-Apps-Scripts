import unittest
from unittest.mock import patch, Mock, call
from settings import DB_USER_MASA, DB_PASSWORD_MASA
import mysql.connector
from tests.code.code_1 import check as check_code1
from tests.code.code_2 import check as check_code2
from tests.crypto.crypto_1 import check as check_crypto1
from tests.crypto.crypto_3 import check as check_crypto3
from tests.network.network_1 import check as check_network1
from tests.network.network_2 import check as check_network2
from tests.network.network_3 import check as check_network3
from tests.platform.platform_2 import check as check_platform2
from tests.platform.platform_3 import check as check_platform3
from tests.storage.storage_2 import check as check_storage2

class TestDatabaseUtils(unittest.TestCase):

    def setUp(self):
        # Conectar a la base de datos de prueba
        self.cnx = mysql.connector.connect(user=DB_USER_MASA, password=DB_PASSWORD_MASA)
        self.cursor = self.cnx.cursor()

    def get_result_TC(self, func_check, tc_name):
        data = {'wdir': './unit_tests/reference_apk/Bluetooth', 'apk': 'base.apk', 'apk_hash': '56c85552ff7034997435761e9b0bd2ef05ea8e2d686423b13a005032c9237f73', 'package_name': 'com.android.bluetooth', 'uuid_execution': '55555555-4444-3333-2222-111111111111'}
        result_TC = func_check(**data)
        
        query = f"""SELECT r.{tc_name}, tfc.{tc_name} FROM Report r INNER JOIN Total_Fail_Counts tfc WHERE r.HASH = tfc.HASH and r.ID_EXECUTION = %s; """
        self.cursor = self.cnx.cursor()
        self.cursor.execute('USE automated_MASA_TESTING')
        self.cursor.execute(query, (data['uuid_execution'],))
        record = self.cursor.fetchall()

        return result_TC, record

    def test_code_1(self):
        result_TC, record = self.get_result_TC(check_code1, 'CODE_1')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_code_2(self):
        result_TC, record = self.get_result_TC(check_code2, 'CODE_2')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_crypto_1(self):
        result_TC, record = self.get_result_TC(check_crypto1, 'CRYPTO_1')

        self.assertEqual(record, [('FAIL', 3)])
        self.assertEqual(result_TC, ['FAIL', 3])

    def test_crypto_3(self):
        result_TC, record = self.get_result_TC(check_crypto3, 'CRYPTO_3')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_network_1(self):
        result_TC, record = self.get_result_TC(check_network1, 'NETWORK_1')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_network_2(self):
        result_TC, record = self.get_result_TC(check_network2, 'NETWORK_2')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_network_3(self):
        result_TC, record = self.get_result_TC(check_network3, 'NETWORK_3')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_platform_2(self):
        result_TC, record = self.get_result_TC(check_platform2, 'PLATFORM_2')

        self.assertEqual(record, [('FAIL', 1)])
        self.assertEqual(result_TC, ['FAIL', 1])

    def test_platform_3(self):
        result_TC, record = self.get_result_TC(check_platform3, 'PLATFORM_3')

        self.assertEqual(record, [('PASS', 0)])
        self.assertEqual(result_TC, ['PASS', 0])

    def test_storage_2(self):
        result_TC, record = self.get_result_TC(check_storage2, 'STORAGE_2')

        self.assertEqual(record, [('FAIL', 2)])
        self.assertEqual(result_TC, ['FAIL', 2])
