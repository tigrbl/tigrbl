from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RustRuntimeHandleRef:
    description: str
    backend: str = "rust"
    metadata: dict[str, Any] = field(default_factory=dict)
