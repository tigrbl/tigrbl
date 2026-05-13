from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import emit_many as _emit_many
from . import shape as _shape

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("fanout", "shape", _shape.ANCHOR, _shape.INSTANCE),
    ("fanout", "emit_many", _emit_many.ANCHOR, _emit_many.INSTANCE),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
