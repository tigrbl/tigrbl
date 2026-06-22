from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _registry_section(name: str) -> dict[str, dict[str, object]]:
    registry = json.loads((ROOT / ".ssot" / "registry.json").read_text())
    return {item["id"]: item for item in registry[name]}


def test_rust_runtime_parity_retirement_t0_registry_contract() -> None:
    features = _registry_section("features")
    claims = _registry_section("claims")
    tests = _registry_section("tests")

    feature = features["feat:rust-runtime-parity-retirement-001"]
    assert feature["implementation_status"] in {"partial", "implemented"}
    assert "spc:2187" in feature["spec_ids"]
    assert "clm:rust-runtime-parity-retirement-001.t0" in feature["claim_ids"]

    claim = claims["clm:rust-runtime-parity-retirement-001.t0"]
    assert claim["tier"] == "T0"
    assert "tst:pytest.rust-runtime-parity-retirement-001.t0.proof-graph" in claim[
        "test_ids"
    ]

    test = tests["tst:pytest.rust-runtime-parity-retirement-001.t0.proof-graph"]
    assert test["path"].endswith(
        "test_rust_runtime_parity_retirement_001_t0_proof_graph.py"
    )
    assert not (ROOT / "pkgs/core/tigrbl_runtime/tigrbl_runtime/rust").exists()
