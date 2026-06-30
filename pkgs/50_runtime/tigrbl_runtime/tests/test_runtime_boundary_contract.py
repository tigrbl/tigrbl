from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = ROOT / "tools" / "ci" / "validate_runtime_boundary.py"
BOUNDARY = ROOT / "pkgs" / "core" / "tigrbl_runtime" / "BOUNDARY.yaml"


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
