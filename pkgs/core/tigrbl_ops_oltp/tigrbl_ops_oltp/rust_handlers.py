from __future__ import annotations

from collections.abc import Callable
from typing import Any
import warnings


def register_rust_handler(name: str, callback: Callable[..., Any]) -> str:
    del callback
    warnings.warn(
        "tigrbl_ops_oltp Rust handler registration is deprecated; handlers are Python-only.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise RuntimeError(f"register_rust_handler({name!r}) is unavailable.")
