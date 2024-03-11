from utils.formula import calculate_formula
import pytest

@pytest.mark.order("last")
def test_check():

    tests = ['CODE_1', 'CODE_2', 'CRYPTO_1', 'CRYPTO_3', 'NETWORK_1', 'NETWORK_2', 'NETWORK_3', 'PLATFORM_2', 'PLATFORM_3', 'STORAGE_2']

    assert calculate_formula(0.01, 0.01, tests, uuid_execution='55555555-4444-3333-2222-111111111111') == 8.6617

