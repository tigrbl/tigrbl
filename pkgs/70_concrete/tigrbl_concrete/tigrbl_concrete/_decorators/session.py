from __future__ import annotations

from typing import Any, Optional
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec, EngineSessionCfg


def _normalize(cfg: Optional[EngineSessionCfg] = None, **kw: Any) -> EngineSessionSpec:
    if cfg is not None and kw:
        raise ValueError("Pass either a mapping/spec or keyword args, not both")
    return EngineSessionSpec.from_any(cfg or kw) or EngineSessionSpec()


def session_ctx(cfg: Optional[EngineSessionCfg] = None, /, **kw: Any):
    """
    Attach a EngineSessionSpec to an App, API, Model/Table, or op handler.

    Precedence is evaluated by the resolver using:
        op > model > router > app
    (Resolver is part of the runtime/engine layer and is independent of this decorator.)
    """
    spec = _normalize(cfg, **kw)

    def _apply(obj: Any) -> Any:
        setattr(obj, "__tigrbl_session_ctx__", spec)
        return obj

    return _apply


def read_only_session(obj: Any = None, /, *, isolation: Optional[str] = None):
    """
    Convenience decorator for read-only sessions.
    """

    def _wrap(o: Any) -> Any:
        setattr(
            o,
            "__tigrbl_session_ctx__",
            EngineSessionSpec(read_only=True, isolation=isolation),
        )
        return o

    return _wrap(obj) if obj is not None else _wrap
