from __future__ import annotations

from typing import Any

from tigrbl_core._compat import warn_legacy_engine_session_name

from .engine_session_spec import (
    EngineSessionCfg,
    EngineSessionSpec,
    engine_session_spec,
    readonly,
    tx_read_committed,
    tx_repeatable_read,
    tx_serializable,
)


def __getattr__(name: str) -> Any:
    if name == "SessionSpec":
        warn_legacy_engine_session_name("SessionSpec", "EngineSessionSpec")
        return EngineSessionSpec
    if name == "SessionCfg":
        warn_legacy_engine_session_name("SessionCfg", "EngineSessionCfg")
        return EngineSessionCfg
    if name == "session_spec":
        warn_legacy_engine_session_name("session_spec", "engine_session_spec")
        return engine_session_spec
    raise AttributeError(name)


__all__ = [
    "EngineSessionCfg",
    "EngineSessionSpec",
    "engine_session_spec",
    "readonly",
    "tx_read_committed",
    "tx_repeatable_read",
    "tx_serializable",
    "SessionCfg",
    "SessionSpec",
    "session_spec",
]
