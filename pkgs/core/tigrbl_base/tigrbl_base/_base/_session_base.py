from __future__ import annotations

from typing import Any

from tigrbl_core._compat import warn_legacy_engine_session_name

from ._engine_session_base import EngineSessionBase


def __getattr__(name: str) -> Any:
    if name == "TigrblSessionBase":
        warn_legacy_engine_session_name("TigrblSessionBase", "EngineSessionBase")
        return EngineSessionBase
    raise AttributeError(name)


__all__ = ["EngineSessionBase", "TigrblSessionBase"]
