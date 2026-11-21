from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = ROOT / "tools" / "ci" / "validate_runtime_boundary.py"
BOUNDARY = Path(__file__).resolve().parents[1] / "BOUNDARY.yaml"


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_runtime_boundary", VALIDATOR
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_runtime_boundary_yaml_exists() -> None:
    assert BOUNDARY.exists()


def test_runtime_boundary_validator_passes() -> None:
    module = _load_validator()
    module.validate()


def test_runtime_boundary_rejects_eager_optional_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_validator()
    source = tmp_path / "dispatcher.py"
    source.write_text(
        "try:\n    from numba import njit\nexcept ImportError:\n    pass\n",
        encoding="utf-8",
    )
    boundary = module._load_boundary()
    boundary["allowed_runtime_files"] = [source.name]
    monkeypatch.setattr(module, "RUNTIME_ROOT", tmp_path)
    monkeypatch.setattr(module, "_load_boundary", lambda: boundary)

    with pytest.raises(AssertionError, match="Runtime loads optional imports.*numba"):
        module.validate()
