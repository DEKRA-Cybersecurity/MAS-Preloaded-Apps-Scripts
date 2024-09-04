import subprocess
import pytest


@pytest.mark.order("first")
def test_check():
    output = subprocess.check_output('./run.sh True', shell=True).splitlines()

    output_str = output[-1].decode("utf-8")

    assert output_str == 'Analysis successfully executed'
