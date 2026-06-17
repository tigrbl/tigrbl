from __future__ import annotations

import pytest

from tigrbl_runtime import Runtime, RustBindingsUnavailableError


def test_rust_runtime_engine_policy_is_unavailable() -> None:
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            Runtime(executor_backend="rust")
