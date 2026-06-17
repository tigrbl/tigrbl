from __future__ import annotations

import pytest

from tigrbl_runtime import (
    Runtime,
    RustBindingsUnavailableError,
    clear_rust_boundary_events,
    compiled_extension_available,
    rust_available,
    rust_boundary_events,
)


def test_rust_runtime_public_surface_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning):
        assert rust_available() is False
    with pytest.warns(DeprecationWarning):
        assert compiled_extension_available() is False
    with pytest.warns(DeprecationWarning):
        clear_rust_boundary_events()
    with pytest.warns(DeprecationWarning):
        assert rust_boundary_events() == []

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            Runtime(executor_backend="rust")


def test_rust_handle_and_execute_rust_are_unavailable() -> None:
    runtime = Runtime()

    with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
        runtime.rust_handle({"name": "runtime-demo"})
    with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
        runtime.execute_rust({"transport": "rest"})
