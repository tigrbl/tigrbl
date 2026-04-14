from __future__ import annotations


def native_atoms_enabled() -> bool:
    try:
        import tigrbl_runtime.native  # noqa: F401
    except Exception:
        return False
    return True
