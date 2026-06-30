"""Error-handling runtime atoms."""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from . import classify as _classify
from . import ctx_build as _ctx_build
from . import rollback as _rollback
from . import transport_shape as _transport_shape

RunFn = Callable[[object | None, Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("err", "ctx_build"): (_ctx_build.ANCHOR, _ctx_build.run),
    ("err", "classify"): (_classify.ANCHOR, _classify.run),
    ("err", "rollback"): (_rollback.ANCHOR, _rollback.run),
    ("err", "transport_shape"): (_transport_shape.ANCHOR, _transport_shape.run),
}

__all__ = ["REGISTRY", "RunFn"]
