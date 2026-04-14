from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RustRequest:
    operation: str = ""
    transport: str = "rest"
    path: str = ""
    method: str = ""
    path_params: dict[str, Any] = field(default_factory=dict)
    query_params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
