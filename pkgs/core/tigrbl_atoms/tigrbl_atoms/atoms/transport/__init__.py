from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import sink_bind as _sink_bind
from . import unit_capture as _unit_capture

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("transport", "unit_capture", _unit_capture.ANCHOR, _unit_capture.INSTANCE),
    ("transport", "sink_bind", _sink_bind.ANCHOR, _sink_bind.INSTANCE),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
