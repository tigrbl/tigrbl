from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class NativePlan:
    description: str
    backend: str = "rust"
    normalized_spec: str | None = None
    parity_snapshot: dict[str, Any] | None = None
    claimable: bool = False
