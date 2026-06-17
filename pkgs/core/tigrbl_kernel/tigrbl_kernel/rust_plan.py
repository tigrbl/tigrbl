from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import warnings


@dataclass(slots=True)
class RustPlan:
    description: str
    compiled_plan: dict[str, Any] | None = None
    backend: str = "deprecated-rust"
    normalized_spec: str | None = None

    def __post_init__(self) -> None:
        warnings.warn(
            "RustPlan is deprecated; Tigrbl kernel planning is Python-only.",
            DeprecationWarning,
            stacklevel=2,
        )
