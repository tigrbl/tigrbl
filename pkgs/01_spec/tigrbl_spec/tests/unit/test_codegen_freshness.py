from __future__ import annotations

import pytest

from tigrbl_spec.codegen import CodegenFreshnessError, check_generated_model_freshness


def test_codegen_freshness_passes_for_packaged_models() -> None:
    check_generated_model_freshness()


def test_codegen_freshness_detects_model_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tigrbl_spec.codegen.spec_kinds", lambda version: ("AppSpec", "NewSpec"))

    with pytest.raises(CodegenFreshnessError, match="NewSpec"):
        check_generated_model_freshness()
