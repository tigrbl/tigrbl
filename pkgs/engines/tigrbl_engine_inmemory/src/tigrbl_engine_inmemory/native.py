from __future__ import annotations

from typing import Any

try:
    from tigrbl_runtime.native import register_python_engine
except Exception:  # pragma: no cover - additive optional integration
    register_python_engine = None


def register_native_engine(kind: str = "inmemory", callback: Any | None = None) -> str:
    if register_python_engine is None:
        return f"python-engine:{kind}"
    return register_python_engine(kind, callback)
