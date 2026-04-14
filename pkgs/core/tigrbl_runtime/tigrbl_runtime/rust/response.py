from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RustResponse:
    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
