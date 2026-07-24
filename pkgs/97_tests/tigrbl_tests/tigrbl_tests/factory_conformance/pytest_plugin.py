from __future__ import annotations

import pytest

from .manifest import load_manifest


@pytest.fixture(scope="session")
def factory_manifest():
    """Return the validated repository factory-surface manifest."""
    return load_manifest()
