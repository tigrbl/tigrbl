"""Compatibility module for ``tigrbl.session.base``."""

from __future__ import annotations

from typing import Any

from tigrbl_core._compat import warn_legacy_engine_session_name
from tigrbl_base._base import EngineSessionBase


def __getattr__(name: str) -> Any:
    if name == "TigrblSessionBase":
        warn_legacy_engine_session_name(
            "tigrbl.session.base.TigrblSessionBase", "EngineSessionBase"
        )
        return EngineSessionBase
    raise AttributeError(name)


__all__ = ["EngineSessionBase", "TigrblSessionBase"]
