from __future__ import annotations

import pytest

import tigrbl_atoms
import tigrbl_runtime
from tigrbl_atoms.fallback import rust_atoms_enabled
from tigrbl_atoms.rust import register_rust_atom, register_rust_callback, register_rust_hook
from tigrbl_runtime import Runtime
from tigrbl_runtime.rust import (
    RustBindingsUnavailableError,
    clear_ffi_boundary_events,
    create_runtime,
    ffi_boundary_events,
    rust_available,
)


def test_rust_runtime_parity_retirement_t1_public_facades() -> None:
    runtime_blocked = {
        "ExecutionBackend",
        "RustBackendConfig",
        "RustBindingsUnavailableError",
        "RustRuntimeHandle",
        "RustRuntimeHandleRef",
        "clear_rust_boundary_events",
        "compiled_extension_available",
        "rust_available",
        "rust_boundary_events",
    }
    atoms_blocked = {
        "rust_atoms_enabled",
        "register_rust_atom",
        "register_rust_callback",
        "register_rust_hook",
    }

    assert runtime_blocked.isdisjoint(tigrbl_runtime.__all__)
    assert atoms_blocked.isdisjoint(tigrbl_atoms.__all__)
    for name in runtime_blocked:
        assert not hasattr(tigrbl_runtime, name)
    for name in atoms_blocked:
        assert not hasattr(tigrbl_atoms, name)


def test_rust_runtime_parity_retirement_t1_shims_fail_closed() -> None:
    with pytest.warns(DeprecationWarning):
        assert rust_available() is False
    with pytest.warns(DeprecationWarning):
        clear_ffi_boundary_events()
    with pytest.warns(DeprecationWarning):
        assert ffi_boundary_events() == []
    with pytest.warns(DeprecationWarning):
        assert rust_atoms_enabled() is False

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            create_runtime({"name": "runtime-demo"})
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            Runtime(executor_backend="rust")

    for registrar in (register_rust_atom, register_rust_callback, register_rust_hook):
        with pytest.warns(DeprecationWarning):
            with pytest.raises(RuntimeError, match="Python-only"):
                registrar("demo", lambda ctx: ctx)
