from pathlib import Path

import pytest


def pytest_collection_modifyitems(items):
    perf_root = Path(__file__).resolve().parent
    for item in items:
        item_path = Path(str(item.path)).resolve()
        if perf_root in item_path.parents:
            item.add_marker(pytest.mark.perf)
