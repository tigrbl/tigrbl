from __future__ import annotations

from typing import Any

from tigrbl_core._compat import warn_legacy_engine_session_name

from ._engine_session import EngineSession, wrap_sessionmaker


def __getattr__(name: str) -> Any:
    if name == "DefaultSession":
        warn_legacy_engine_session_name("DefaultSession", "EngineSession")
        return EngineSession
    raise AttributeError(name)


__all__ = ["EngineSession", "wrap_sessionmaker", "DefaultSession"]
