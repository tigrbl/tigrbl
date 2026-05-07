from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic_ns
from typing import Any


@dataclass(frozen=True, slots=True)
class BatchPolicy:
    enabled: bool = False
    max_size: int = 64
    max_bytes: int = 1_048_576
    max_delay_ms: int = 1
    admission_timeout_ms: int = 5
    conflict_policy: str = "single_fallback"
    overflow_policy: str = "backpressure"
    result_fanout: str = "by_admission"
    allow_reads: bool = False
    max_queue_depth: int = 1024
    max_in_flight: int = 16


@dataclass(slots=True)
class BatchAdmission:
    admission_id: int
    group_key: tuple[Any, ...]
    intent: dict[str, Any]
    sink: Any
    sink_index: int
    size_bytes: int = 0
    status: str = "admitted"
    rejection_reason: str | None = None
    result_index: int | None = None
    future: Any | None = None
    slot_payload: Any | None = None
    parameter_row: tuple[Any, ...] | None = None


@dataclass(slots=True)
class BatchGroup:
    group_key: tuple[Any, ...]
    admissions: list[BatchAdmission] = field(default_factory=list)
    sealed: bool = False
    created_ns: int = field(default_factory=monotonic_ns)
    size_bytes: int = 0
    fallback: bool = False
    fallback_reason: str | None = None
    result_slots: list[Any] = field(default_factory=list)
    error_slots: list[Any] = field(default_factory=list)
    owner_admission_id: int | None = None
    parameter_columns: tuple[str, ...] = ()
    parameter_rows: list[tuple[Any, ...]] = field(default_factory=list)
