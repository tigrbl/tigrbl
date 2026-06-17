from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FEATURE_ID = "feat:rust-kernel-surface-retirement-001"
CLAIM_ID = "clm:rust-kernel-surface-retirement-001.t2"
EVIDENCE_ID = "evd:t2.rust-kernel-surface-retirement-001.proof-graph"
EXPECTED_TESTS = {
    "tst:pytest.rust-kernel-surface-retirement-001.t2.proof-graph",
    "tst:python-only-runtime-rust-kernel-module-retirement",
}


def _section(name: str) -> dict[str, dict[str, object]]:
    registry = json.loads((ROOT / ".ssot" / "registry.json").read_text())
    return {item["id"]: item for item in registry[name]}


def test_rust_kernel_surface_retirement_t2_proof_graph_is_closed() -> None:
    features = _section("features")
    claims = _section("claims")
    evidence = _section("evidence")
    tests = _section("tests")

    feature = features[FEATURE_ID]
    claim = claims[CLAIM_ID]

    assert feature["implementation_status"] == "implemented"
    assert claim["tier"] == "T2"
    assert claim["status"] == "evidenced"
    assert EXPECTED_TESTS.issubset(set(claim["test_ids"]))
    assert evidence[EVIDENCE_ID]["status"] == "passed"

    for test_id in EXPECTED_TESTS:
        test = tests[test_id]
        assert test["status"] == "passing"
        assert (ROOT / test["path"]).exists()
