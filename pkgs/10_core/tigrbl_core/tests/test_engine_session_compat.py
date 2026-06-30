from __future__ import annotations

import importlib

import pytest

from tigrbl_core import _compat
from tigrbl_core._spec.engine_session_spec import EngineSessionCfg, EngineSessionSpec


legacy_session_spec = importlib.import_module("tigrbl_core._spec.session_spec")


def test_legacy_session_spec_names_warn_before_removal() -> None:
    with pytest.warns(DeprecationWarning, match="SessionSpec is deprecated"):
        assert legacy_session_spec.__getattr__("SessionSpec") is EngineSessionSpec

    with pytest.warns(DeprecationWarning, match="SessionCfg is deprecated"):
        assert legacy_session_spec.__getattr__("SessionCfg") is EngineSessionCfg


def test_legacy_engine_session_names_fail_after_removal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_compat, "_dist_version_tuple", lambda: (0, 13, 1))

    with pytest.raises(RuntimeError, match="removed after tigrbl 0.13.0"):
        _compat.warn_legacy_engine_session_name("SessionSpec", "EngineSessionSpec")
