from __future__ import annotations


def native_handlers_enabled() -> bool:
    try:
        import tigrbl_native  # noqa: F401
    except Exception:
        return False
    return True
