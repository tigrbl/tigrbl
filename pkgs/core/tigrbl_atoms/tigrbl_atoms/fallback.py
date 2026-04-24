from __future__ import annotations

from importlib import import_module


def rust_atoms_enabled() -> bool:
    try:
        import_module("tigrbl_runtime.rust")
    except Exception:
        return False
    return True
