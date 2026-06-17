from __future__ import annotations

import warnings


def rust_handlers_enabled() -> bool:
    warnings.warn(
        "tigrbl_ops_oltp Rust handler registration is deprecated; handlers are Python-only.",
        DeprecationWarning,
        stacklevel=2,
    )
    return False
