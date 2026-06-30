from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import build as _build
from . import final_group_key as _final_group_key
from . import prekey as _prekey

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("intent", "build", _build.ANCHOR, _build.INSTANCE),
    ("intent", "prekey", _prekey.ANCHOR, _prekey.INSTANCE),
    (
        "intent",
        "final_group_key",
        _final_group_key.ANCHOR,
        _final_group_key.INSTANCE,
    ),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
