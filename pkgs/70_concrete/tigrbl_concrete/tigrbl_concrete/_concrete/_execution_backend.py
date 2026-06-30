from __future__ import annotations

from typing import Any


def normalize_execution_backend(value: Any) -> str:
    lowered = str(value or "auto").strip().lower()
    if not lowered:
        return "auto"
    if lowered in {"auto", "python"}:
        return lowered
    raise ValueError(f"unsupported execution backend: {value!r}")
