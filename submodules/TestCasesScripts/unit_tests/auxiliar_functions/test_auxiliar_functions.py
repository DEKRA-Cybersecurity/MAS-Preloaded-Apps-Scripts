import unittest
from unittest.mock import patch
from utils.auxiliar_functions import check_signature, check_debuggable, check_package_name, check_hash_apk, get_suid_from_manifest, check_network_applies, get_version_name, parse_timestamp

class TestAuxiliarFunctions(unittest.TestCase):

    def setUp(self):
        # Conectar a la base de datos de prueba
        self.wdir = './unit_tests/reference_apk/Bluetooth'
        self.apk = 'base.apk'
        self.apk_hash = '56c85552ff7034997435761e9b0bd2ef05ea8e2d686423b13a005032c9237f73'
        self.package_name = 'com.android.bluetooth'
        self.name = 'Bluetooth'
        self.internet = '1'
        self.uuid_execution = '55555555-4444-3333-2222-111111111111'
        self.timestamp = '2024-02-27 16:29:35.256314'

    def test_check_signature(self):
        # Simulate a successful verification scenario
        expected_output = [
            'Verifies',
            'Verified using v1 scheme (JAR signing): false',
            'Verified using v2 scheme (APK Signature Scheme v2): false',
            'Verified using v3 scheme (APK Signature Scheme v3): true',
            'Verified using v3.1 scheme (APK Signature Scheme v3.1): false',
            'Verified using v4 scheme (APK Signature Scheme v4): false',
            'Verified for SourceStamp: false',
            'Number of signers: 1',
        ]
        
        output = check_signature(self.wdir, self.apk, self.apk_hash, self.package_name, self.uuid_execution)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_check_debuggable(self):
        # Simulate a successful verification scenario
        expected_output = "No relevant results"

        output = check_debuggable(self.wdir, self.apk_hash, self.package_name, self.uuid_execution)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_check_package_name(self):
        # Simulate a successful verification scenario
        expected_output = "com.android.bluetooth"

        output = check_package_name(self.wdir, self.name)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_check_hash_apk(self):
        # Simulate a successful verification scenario
        expected_output = self.apk_hash

        output = check_hash_apk(self.wdir)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_get_suid_from_manifest(self):
        # Simulate a successful verification scenario
        expected_output = "android.uid.bluetooth"

        output = get_suid_from_manifest(self.wdir)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_check_network_applies(self):
        # Simulate a successful verification scenario
        expected_output = True

        output = check_network_applies(self.wdir, self.apk_hash, self.internet, self.uuid_execution)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_get_version_name(self):
        # Simulate a successful verification scenario
        expected_output = '13'
        
        output = get_version_name(self.wdir)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

    def test_parse_timestamp(self):
        # Simulate a successful verification scenario
        expected_output = '20240227_162935_256'
        
        output = parse_timestamp(self.timestamp)

        # Assert that the output matches the expected output
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()