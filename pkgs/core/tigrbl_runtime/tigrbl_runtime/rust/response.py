from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import warnings


@dataclass(slots=True)
class RustResponse:
    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None

    def __post_init__(self) -> None:
        warnings.warn(
            "RustResponse is deprecated; Tigrbl runtime execution is Python-only.",
            DeprecationWarning,
            stacklevel=2,
        )

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
