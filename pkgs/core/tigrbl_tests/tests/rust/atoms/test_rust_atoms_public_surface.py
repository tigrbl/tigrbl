from __future__ import annotations

from tigrbl_atoms import (
    rust_atoms_enabled,
    register_rust_atom,
    register_rust_hook,
)
from tigrbl_runtime import clear_rust_boundary_events, rust_boundary_events


def test_rust_atom_and_hook_registrars_round_trip_through_binding_trace() -> None:
    clear_rust_boundary_events()
    atom_descriptor = register_rust_atom("demo.atom", lambda ctx: ctx)
    hook_descriptor = register_rust_hook("demo.hook", lambda ctx: ctx)

    assert rust_atoms_enabled() is True
    assert atom_descriptor == "python-atom:demo.atom"
    assert hook_descriptor == "python-hook:demo.hook"

    names = [item["event"] for item in rust_boundary_events()]
    assert names[-2:] == ["register_python_atom", "register_python_hook"]
