from pathlib import Path
from runpy import run_path

import pytest


@pytest.mark.parametrize("name", ["quick_start.py", "usage.py"])
def test_example(name):
    run_path(str(Path(__file__).with_name(name)))
