from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / ".ssot" / "registry.json"

FEATURES = {
    "feat:python-runtime-ddl-initialization-boundary-001": {"spc:2086"},
    "feat:rust-runtime-ddl-initialization-boundary-001": {"spc:2086"},
    "feat:python-request-hot-path-no-ddl-001": {"spc:2086", "spc:2088"},
    "feat:rust-request-hot-path-no-ddl-001": {"spc:2086", "spc:2088"},
    "feat:python-schema-readiness-fail-closed-001": {"spc:2086"},
    "feat:rust-schema-readiness-fail-closed-001": {"spc:2086"},
    "feat:python-engine-session-lifecycle-001": {"spc:2087"},
    "feat:rust-engine-session-lifecycle-001": {"spc:2087"},
    "feat:python-transaction-hot-path-001": {"spc:2087", "spc:2088"},
    "feat:rust-transaction-hot-path-001": {"spc:2087", "spc:2088"},
    "feat:python-runtime-performance-baseline-001": {"spc:2088"},
    "feat:rust-runtime-performance-baseline-001": {"spc:2088"},
    "feat:python-runtime-callgraph-export-001": {"spc:2088"},
    "feat:rust-runtime-callgraph-export-001": {"spc:2088"},
    "feat:python-direct-runtime-microbench-001": {"spc:2088"},
    "feat:rust-direct-runtime-microbench-001": {"spc:2088"},
    "feat:python-request-envelope-contract-001": {"spc:2089"},
    "feat:rust-request-envelope-contract-001": {"spc:2089"},
    "feat:python-asgi-boundary-evidence-001": {"spc:2088", "spc:2089"},
    "feat:rust-asgi-boundary-evidence-001": {"spc:2088", "spc:2089"},
    "feat:python-runtime-2x-target-comparison-001": {"spc:2088"},
    "feat:rust-runtime-2x-python-target-001": {"spc:2088"},
}

ADRS = {"adr:1083", "adr:1084", "adr:1085", "adr:1086"}
SPECS = {"spc:2086", "spc:2087", "spc:2088", "spc:2089"}


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_runtime_python_rust_governance_documents_exist() -> None:
    registry = _registry()
    adrs = {item["id"]: item for item in registry["adrs"]}
    specs = {item["id"]: item for item in registry["specs"]}

    assert ADRS <= set(adrs)
    assert SPECS <= set(specs)
    assert all(adrs[adr_id]["status"] == "accepted" for adr_id in ADRS)
    assert all(specs[spec_id]["status"] == "accepted" for spec_id in SPECS)


def test_runtime_python_rust_features_are_spec_aware_pairs() -> None:
    registry = _registry()
    features = {item["id"]: item for item in registry["features"]}

    for feature_id, spec_ids in FEATURES.items():
        feature = features[feature_id]
        assert set(feature["spec_ids"]) == spec_ids
        assert feature["implementation_status"] == "absent"
        assert feature["plan"]["horizon"] == "next"
        assert feature["plan"]["target_claim_tier"] == "T2"
        assert feature["plan"]["target_lifecycle_stage"] == "active"


def test_runtime_python_rust_features_have_verification_edges() -> None:
    registry = _registry()
    features = {item["id"]: item for item in registry["features"]}

    for feature_id in FEATURES:
        feature = features[feature_id]
        assert feature["test_ids"], feature_id
        assert feature["claim_ids"], feature_id
