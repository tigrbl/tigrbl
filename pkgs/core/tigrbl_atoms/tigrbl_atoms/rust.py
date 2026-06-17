from __future__ import annotations

from collections.abc import Callable
from typing import Any
import warnings


def _raise_deprecated(name: str) -> str:
    warnings.warn(
        "tigrbl_atoms Rust registration is deprecated; atoms are Python-only.",
        DeprecationWarning,
        stacklevel=3,
    )
    raise RuntimeError(f"{name} is unavailable; Tigrbl atoms are Python-only.")


def register_rust_callback(name: str, callback: Callable[..., Any]) -> str:
    del callback
    return _raise_deprecated(f"register_rust_callback({name!r})")


def register_rust_atom(name: str, callback: Callable[..., Any]) -> str:
    del callback
    return _raise_deprecated(f"register_rust_atom({name!r})")


def register_rust_hook(name: str, callback: Callable[..., Any]) -> str:
    del callback
    return _raise_deprecated(f"register_rust_hook({name!r})")
