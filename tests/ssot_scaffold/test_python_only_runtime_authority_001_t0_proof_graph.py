from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _registry_section(name: str) -> dict[str, dict[str, object]]:
    registry = json.loads((ROOT / ".ssot" / "registry.json").read_text())
    return {item["id"]: item for item in registry[name]}


def test_python_only_runtime_authority_t0_registry_contract() -> None:
    features = _registry_section("features")
    claims = _registry_section("claims")
    specs = _registry_section("specs")
    tests = _registry_section("tests")

    feature = features["feat:python-only-runtime-authority-001"]
    assert feature["implementation_status"] in {"partial", "implemented"}
    assert "spc:2187" in feature["spec_ids"]
    assert "clm:python-only-runtime-authority-001.t0" in feature["claim_ids"]

    claim = claims["clm:python-only-runtime-authority-001.t0"]
    assert claim["tier"] == "T0"
    assert "tst:pytest.python-only-runtime-authority-001.t0.proof-graph" in claim[
        "test_ids"
    ]

    spec = specs["spc:2187"]
    assert spec["status"] == "accepted"
    assert "Python-only runtime" in spec["title"]

    test = tests["tst:pytest.python-only-runtime-authority-001.t0.proof-graph"]
    assert test["path"] == (
        Path("tests/ssot_scaffold/test_python_only_runtime_authority_001_t0_proof_graph.py")
        .as_posix()
    )
    assert (ROOT / "pkgs/core/tigrbl_runtime/tigrbl_runtime/runtime/runtime.py").exists()
