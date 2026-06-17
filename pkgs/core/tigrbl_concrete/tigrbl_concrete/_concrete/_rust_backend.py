from __future__ import annotations

from typing import Any
import warnings


def normalize_execution_backend(value: Any) -> str:
    if value is None:
        return "auto"
    lowered = str(value).strip().lower()
    if lowered == "rust":
        raise ValueError(
            "execution_backend='rust' is deprecated and unavailable; "
            "Tigrbl runtime execution is Python-only."
        )
    if lowered not in {"auto", "python"}:
        raise ValueError(f"unsupported execution backend: {value!r}")
    return lowered


def ffi_boundary_events() -> list[dict[str, Any]]:
    warnings.warn(
        "Rust boundary tracing is deprecated; Tigrbl runtime execution is Python-only.",
        DeprecationWarning,
        stacklevel=2,
    )
    return []


def clear_ffi_boundary_events() -> None:
    warnings.warn(
        "Rust boundary tracing is deprecated; Tigrbl runtime execution is Python-only.",
        DeprecationWarning,
        stacklevel=2,
    )
    return None
