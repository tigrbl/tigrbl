from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .errors import raise_rust_deprecated, warn_rust_deprecated


class ExecutionBackend(str, Enum):
    AUTO = "auto"
    PYTHON = "python"
    RUST = "rust"


@dataclass(slots=True, frozen=True)
class RustBackendConfig:
    backend: ExecutionBackend = ExecutionBackend.AUTO
    allow_python_callbacks: bool = True
    emit_boundary_trace: bool = False
    strict_rust: bool = False


def coerce_execution_backend(value: str | ExecutionBackend | None) -> ExecutionBackend:
    if isinstance(value, ExecutionBackend):
        if value is ExecutionBackend.RUST:
            warn_rust_deprecated()
        return value
    if value is None:
        return ExecutionBackend.AUTO
    lowered = str(value).strip().lower()
    for item in ExecutionBackend:
        if item.value == lowered:
            if item is ExecutionBackend.RUST:
                warn_rust_deprecated()
            return item
    raise ValueError(f"unsupported execution backend: {value!r}")


def wants_rust_backend(value: str | ExecutionBackend | RustBackendConfig | None) -> bool:
    if isinstance(value, RustBackendConfig):
        backend = value.backend
    else:
        backend = coerce_execution_backend(value)
    if backend is ExecutionBackend.RUST:
        warn_rust_deprecated()
    return False


def reject_rust_backend(
    value: str | ExecutionBackend | RustBackendConfig | None,
    *,
    label: str,
) -> ExecutionBackend:
    if isinstance(value, RustBackendConfig):
        if value.strict_rust:
            raise_rust_deprecated(f"{label}.strict_rust")
        backend = value.backend
    else:
        backend = coerce_execution_backend(value)
    if backend is ExecutionBackend.RUST:
        raise_rust_deprecated(label)
    return backend
