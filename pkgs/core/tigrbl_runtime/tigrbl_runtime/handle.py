from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import warnings


@dataclass(slots=True)
class RustRuntimeHandleRef:
    description: str
    backend: str = "deprecated-rust"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        warnings.warn(
            "RustRuntimeHandleRef is deprecated; Tigrbl runtime execution is Python-only.",
            DeprecationWarning,
            stacklevel=2,
        )
