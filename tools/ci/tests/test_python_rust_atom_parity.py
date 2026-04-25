from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def _run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/ci/python_rust_atom_parity.py", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_python_rust_atom_parity_registry_is_complete() -> None:
    result = _run_validator("--validate")
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_python_rust_atom_parity_reports_exist_and_match_registry() -> None:
    inventory = json.loads((ROOT / ".ssot/reports/python-rust-atom-parity-inventory.json").read_text(encoding="utf-8"))
    feature_map = json.loads((ROOT / ".ssot/reports/python-rust-parity-feature-map.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / ".ssot/registry.json").read_text(encoding="utf-8"))
    features = {item["id"] for item in registry["features"]}

    assert inventory["unit_count"] == len(feature_map["features"])
    assert inventory["matched_count"] > 0
    assert feature_map["boundary_id"] == "bnd:python-rust-fully-paritable-suite-001"
    assert all(item["feature_id"] in features for item in feature_map["features"])


def test_python_rust_parity_evidence_paths_are_fresh() -> None:
    registry = json.loads((ROOT / ".ssot/registry.json").read_text(encoding="utf-8"))
    evidence = [item for item in registry["evidence"] if item["id"].startswith("evd:python-rust-")]
    assert evidence
    for item in evidence:
        assert item["status"] == "passed"
        assert (ROOT / item["path"]).exists(), item["path"]
