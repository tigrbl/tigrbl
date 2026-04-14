from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from tigrbl_runtime.rust import register_python_handler
except Exception:  # pragma: no cover - additive optional integration
    register_python_handler = None


def register_rust_handler(name: str, callback: Callable[..., Any]) -> str:
    if register_python_handler is None:
        return f"python-handler:{name}"
    return register_python_handler(name, callback)
