from __future__ import annotations

from tigrbl_atoms import (
    native_atoms_enabled,
    register_native_atom,
    register_native_hook,
)
from tigrbl_native import clear_ffi_boundary_events, ffi_boundary_events


def test_native_atom_and_hook_registrars_round_trip_through_binding_trace() -> None:
    clear_ffi_boundary_events()
    atom_descriptor = register_native_atom("demo.atom", lambda ctx: ctx)
    hook_descriptor = register_native_hook("demo.hook", lambda ctx: ctx)

    assert native_atoms_enabled() is True
    assert atom_descriptor == "python-atom:demo.atom"
    assert hook_descriptor == "python-hook:demo.hook"

    names = [item["event"] for item in ffi_boundary_events()]
    assert names[-2:] == ["register_python_atom", "register_python_hook"]
