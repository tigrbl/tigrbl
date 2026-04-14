from __future__ import annotations


def rust_handlers_enabled() -> bool:
    try:
        import tigrbl_runtime.rust  # noqa: F401
    except Exception:
        return False
    return True
