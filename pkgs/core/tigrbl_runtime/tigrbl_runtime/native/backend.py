from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionBackend(str, Enum):
    AUTO = "auto"
    PYTHON = "python"
    RUST = "rust"


@dataclass(slots=True, frozen=True)
class NativeBackendConfig:
    backend: ExecutionBackend = ExecutionBackend.AUTO
    allow_python_callbacks: bool = True
    emit_boundary_trace: bool = False
    strict_native: bool = False


def coerce_execution_backend(value: str | ExecutionBackend | None) -> ExecutionBackend:
    if isinstance(value, ExecutionBackend):
        return value
    if value is None:
        return ExecutionBackend.AUTO
    lowered = str(value).strip().lower()
    for item in ExecutionBackend:
        if item.value == lowered:
            return item
    raise ValueError(f"unsupported execution backend: {value!r}")


def wants_native_backend(value: str | ExecutionBackend | NativeBackendConfig | None) -> bool:
    if isinstance(value, NativeBackendConfig):
        backend = value.backend
    else:
        backend = coerce_execution_backend(value)
    return backend in {ExecutionBackend.AUTO, ExecutionBackend.RUST}
