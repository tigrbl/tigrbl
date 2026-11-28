from __future__ import annotations

import importlib.util

import tigrbl
import tigrbl_atoms
import tigrbl_kernel
import tigrbl_runtime


RUST_PUBLIC_NAMES = {
    "ExecutionBackend",
    "RustBackendConfig",
    "RustBindingsUnavailableError",
    "RustPlan",
    "RustRuntimeHandle",
    "RustRuntimeHandleRef",
    "build_rust_kernel",
    "clear_rust_boundary_events",
    "compiled_extension_available",
    "normalize_rust_spec",
    "register_rust_atom",
    "register_rust_callback",
    "register_rust_hook",
    "rust_atoms_enabled",
    "rust_available",
    "rust_boundary_events",
}


def test_public_facades_do_not_advertise_rust_runtime_surfaces() -> None:
    for module in (tigrbl, tigrbl_atoms, tigrbl_kernel, tigrbl_runtime):
        exported = set(getattr(module, "__all__", ()))
        assert RUST_PUBLIC_NAMES.isdisjoint(exported), module.__name__


def test_public_facades_do_not_resolve_rust_runtime_surfaces() -> None:
    for module in (tigrbl_atoms, tigrbl_kernel, tigrbl_runtime):
        for name in RUST_PUBLIC_NAMES:
            assert not hasattr(module, name), f"{module.__name__}.{name}"


def test_retired_rust_modules_are_not_importable() -> None:
    for module_name in (
        "tigrbl_runtime.rust",
        "tigrbl_kernel.rust_compile",
        "tigrbl_kernel.rust_plan",
        "tigrbl_kernel.rust_spec",
        "tigrbl_atoms.rust",
        "tigrbl_atoms.fallback",
    ):
        assert importlib.util.find_spec(module_name) is None
