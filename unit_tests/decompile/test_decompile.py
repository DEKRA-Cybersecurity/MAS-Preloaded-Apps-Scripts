import subprocess
import pytest

@pytest.mark.order("first")
def test_check():
    output = subprocess.check_output('./automate_apps_updated False', shell=True).splitlines()

    output_str=output[-1].decode("utf-8")

    assert output_str == 'Analysis successfully executed'