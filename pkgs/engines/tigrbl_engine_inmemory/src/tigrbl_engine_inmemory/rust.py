from __future__ import annotations

from typing import Any
import warnings


def register_rust_engine(kind: str = "inmemory", callback: Any | None = None) -> str:
    del callback
    warnings.warn(
        "tigrbl_engine_inmemory Rust registration is deprecated; engines are Python-only.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise RuntimeError(f"register_rust_engine({kind!r}) is unavailable.")
