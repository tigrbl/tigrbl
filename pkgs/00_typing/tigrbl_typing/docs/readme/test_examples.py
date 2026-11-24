"""Python compilation and other example-file presence; no runtime certification."""

from pathlib import Path
import pytest


@pytest.mark.unit
def test_readme_example_sources():
    root = Path(__file__).resolve().parents[2]
    for relative in ("docs/readme/quick_start.py", "docs/readme/usage.py"):
        source = root / relative
        assert source.is_file() and source.read_text("utf-8").strip()
        if source.suffix == ".py":
            compile(source.read_text("utf-8"), str(source), "exec")
