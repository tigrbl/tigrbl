from __future__ import annotations

import importlib.util

import tigrbl_atoms
import tigrbl_runtime
from tigrbl_runtime import Runtime


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


def test_rust_runtime_parity_retirement_t1_shims_are_removed() -> None:
    assert importlib.util.find_spec("tigrbl_runtime.rust") is None
    assert importlib.util.find_spec("tigrbl_atoms.rust") is None
    assert importlib.util.find_spec("tigrbl_atoms.fallback") is None

    runtime = Runtime(executor_backend="python")
    assert runtime.executor_backend == "python"
    assert not hasattr(runtime, "rust_handle")
    assert not hasattr(runtime, "execute_rust")
