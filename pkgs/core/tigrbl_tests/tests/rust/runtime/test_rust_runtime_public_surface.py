from __future__ import annotations

import pytest

from tigrbl_runtime import Runtime
from tigrbl_runtime.rust import (
    RustBindingsUnavailableError,
    clear_ffi_boundary_events,
    compiled_extension_available,
    ffi_boundary_events,
    rust_available,
)


def test_rust_runtime_public_surface_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning):
        assert rust_available() is False
    with pytest.warns(DeprecationWarning):
        assert compiled_extension_available() is False
    with pytest.warns(DeprecationWarning):
        clear_ffi_boundary_events()
    with pytest.warns(DeprecationWarning):
        assert ffi_boundary_events() == []

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            Runtime(executor_backend="rust")


def test_rust_handle_and_execute_rust_are_unavailable() -> None:
    runtime = Runtime()

    with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
        runtime.rust_handle({"name": "runtime-demo"})
    with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
        runtime.execute_rust({"transport": "rest"})
