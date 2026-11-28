"""Compatibility module for ``tigrbl.session.spec``."""

from __future__ import annotations

from typing import Any

from tigrbl_core._compat import warn_legacy_engine_session_name
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec


def __getattr__(name: str) -> Any:
    if name == "SessionSpec":
        warn_legacy_engine_session_name("tigrbl.session.spec.SessionSpec", "EngineSessionSpec")
        return EngineSessionSpec
    raise AttributeError(name)


__all__ = ["EngineSessionSpec", "SessionSpec"]
