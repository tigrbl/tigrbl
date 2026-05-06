from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic_ns
from typing import Any


@dataclass(slots=True)
class BatchAdmission:
    admission_id: int
    group_key: tuple[Any, ...]
    intent: dict[str, Any]
    sink: Any
    sink_index: int
    result_index: int | None = None


@dataclass(slots=True)
class BatchGroup:
    group_key: tuple[Any, ...]
    admissions: list[BatchAdmission] = field(default_factory=list)
    sealed: bool = False
    created_ns: int = field(default_factory=monotonic_ns)
    result_slots: list[Any] = field(default_factory=list)
    error_slots: list[Any] = field(default_factory=list)
