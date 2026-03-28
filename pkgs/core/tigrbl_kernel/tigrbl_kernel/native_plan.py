from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NativePlan:
    description: str
    backend: str = "rust"
    normalized_spec: str | None = None
