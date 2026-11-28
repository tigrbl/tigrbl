"""Compatibility exports for legacy ``tigrbl.session`` imports."""

from __future__ import annotations

from typing import Any

from tigrbl_core._compat import warn_legacy_engine_session_name
from tigrbl_base._base import EngineSessionBase
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec


def __getattr__(name: str) -> Any:
    if name == "SessionSpec":
        warn_legacy_engine_session_name("tigrbl.session.SessionSpec", "EngineSessionSpec")
        return EngineSessionSpec
    if name == "TigrblSessionBase":
        warn_legacy_engine_session_name(
            "tigrbl.session.TigrblSessionBase", "EngineSessionBase"
        )
        return EngineSessionBase
    raise AttributeError(name)


__all__ = [
    "EngineSessionSpec",
    "EngineSessionBase",
    "SessionSpec",
    "TigrblSessionBase",
]
