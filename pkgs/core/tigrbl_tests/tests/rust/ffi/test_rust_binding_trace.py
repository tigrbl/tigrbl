from __future__ import annotations

import pytest

from tigrbl_runtime.rust import (
    RustBindingsUnavailableError,
    clear_ffi_boundary_events,
    create_runtime,
    ffi_boundary_events,
)


def test_rust_runtime_trace_helpers_are_deprecated() -> None:
    with pytest.warns(DeprecationWarning):
        clear_ffi_boundary_events()
    with pytest.warns(DeprecationWarning):
        assert ffi_boundary_events() == []

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            create_runtime({"name": "ffi-demo"})
