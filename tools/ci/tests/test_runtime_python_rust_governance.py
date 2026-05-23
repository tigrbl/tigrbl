from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / ".ssot" / "registry.json"
REPORTS = ROOT / ".ssot" / "reports"

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
SPECS = {"spc:2086", "spc:2087", "spc:2088", "spc:2089", "spc:2090"}
PROTOCOL_FEATURES = {
    "feat:protocol-runtime-boundary-certification-001": {
        "spec_ids": {"spc:2085", "spc:2093", "spc:2114", "spc:2140"},
        "claim_id": "clm:protocol-runtime-boundary-certification-001",
        "test_id": "tst:protocol-runtime-boundary-certification-001",
        "evidence_id": "evd:protocol-runtime-boundary-certification-001",
    },
    "feat:protocol-runtime-profile-pack-001": {
        "spec_ids": {"spc:0614", "spc:2058", "spc:2113", "spc:2114"},
        "claim_id": "clm:protocol-runtime-profile-pack-001",
        "test_id": "tst:protocol-runtime-profile-pack-001",
        "evidence_id": "evd:protocol-runtime-profile-pack-001",
    },
    "feat:protocol-runtime-ssot-feature-granularity-001": {
        "spec_ids": {"spc:2084", "spc:2085", "spc:2113", "spc:2114"},
        "claim_id": "clm:protocol-runtime-ssot-feature-granularity-001",
        "test_id": "tst:protocol-runtime-ssot-feature-granularity-001",
        "evidence_id": "evd:protocol-runtime-ssot-feature-granularity-001",
    },
    "feat:protocol-runtime-test-evidence-suite-001": {
        "spec_ids": {"spc:2084", "spc:2085", "spc:2114", "spc:2140"},
        "claim_id": "clm:protocol-runtime-test-evidence-suite-001",
        "test_id": "tst:protocol-runtime-test-evidence-suite-001",
        "evidence_id": "evd:protocol-runtime-test-evidence-suite-001",
    },
    "feat:rust-protocol-plan-parity-001": {
        "spec_ids": {"spc:2090", "spc:2092", "spc:2114", "spc:2140"},
        "claim_id": "clm:rust-protocol-plan-parity-001",
        "test_id": "tst:rust-protocol-plan-parity-001",
        "evidence_id": "evd:rust-protocol-plan-parity-001",
    },
}
PROTOCOL_PROFILE_ID = "prf:tigrbl-runtime-protocol-conformance"
PARITY_REPORTS = {
    REPORTS / "python-rust-atom-parity-inventory.json",
    REPORTS / "python-rust-parity-feature-map.json",
    REPORTS / "python-rust-atom-parity-results.json",
    REPORTS / "python-rust-kernelplan-parity-results.json",
    REPORTS / "python-rust-parity-certification-map.json",
}


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
        assert set(feature["spec_ids"]) == spec_ids | {"spc:2090"}
        assert feature["implementation_status"] == "implemented"
        assert feature["plan"]["horizon"] == "current"
        assert feature["plan"]["target_claim_tier"] == "T2"
        assert feature["plan"]["target_lifecycle_stage"] == "active"


def test_runtime_python_rust_features_have_verification_edges() -> None:
    registry = _registry()
    features = {item["id"]: item for item in registry["features"]}

    for feature_id in FEATURES:
        feature = features[feature_id]
        assert feature["test_ids"], feature_id
        assert feature["claim_ids"], feature_id


def test_runtime_python_rust_evidence_artifacts_exist() -> None:
    perf = ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "perf"
    required = {
        perf / "hot_path_perf_suite_manifest.json",
        perf / "hot_path_perf_suite_report.md",
        perf / "kernel-plan-benchmark.json",
        perf / "kernel-plan-benchmark-websocket.json",
        perf / "kernel-plan-benchmark-webtransport.json",
        perf / "tigrbl_websocket_transport_call_graph_250_ops.json",
        perf / "tigrbl_webtransport_transport_call_graph_250_ops.json",
        perf / "runtime_hotstate_microbench.json",
        perf / "runtime_typecheck_microbench.json",
        perf / "exact_route_marker_microbench.json",
    }

    missing = [path for path in sorted(required) if not path.exists() or path.stat().st_size == 0]
    assert missing == []


def test_protocol_runtime_governance_features_are_closed() -> None:
    registry = _registry()
    features = {item["id"]: item for item in registry["features"]}
    claims = {item["id"]: item for item in registry["claims"]}
    tests = {item["id"]: item for item in registry["tests"]}
    evidence = {item["id"]: item for item in registry["evidence"]}

    for feature_id, expected in PROTOCOL_FEATURES.items():
        feature = features[feature_id]
        claim = claims[expected["claim_id"]]
        test = tests[expected["test_id"]]
        evd = evidence[expected["evidence_id"]]

        assert set(feature["spec_ids"]) == expected["spec_ids"]
        assert feature["implementation_status"] == "implemented"
        assert feature["plan"]["horizon"] == "current"
        assert feature["plan"]["target_claim_tier"] == "T2"
        assert feature["plan"]["target_lifecycle_stage"] == "active"
        assert feature["claim_ids"] == [expected["claim_id"]]
        assert feature["test_ids"] == [expected["test_id"]]

        assert claim["feature_ids"] == [feature_id]
        assert expected["test_id"] in claim["test_ids"]
        assert expected["evidence_id"] in claim["evidence_ids"]

        assert test["status"] == "passing"
        assert feature_id in test["feature_ids"]
        assert expected["claim_id"] in test["claim_ids"]
        assert expected["evidence_id"] in test["evidence_ids"]

        assert evd["status"] == "passed"
        assert expected["claim_id"] in evd["claim_ids"]
        assert expected["test_id"] in evd["test_ids"]
        assert (ROOT / evd["path"]).exists()


def test_protocol_runtime_profile_pack_contains_governed_rows() -> None:
    registry = _registry()
    profiles = {item["id"]: item for item in registry["profiles"]}
    profile = profiles[PROTOCOL_PROFILE_ID]

    assert profile["status"] == "active"
    assert set(PROTOCOL_FEATURES) <= set(profile["feature_ids"])


def test_protocol_runtime_parity_reports_exist() -> None:
    missing = [path for path in sorted(PARITY_REPORTS) if not path.exists() or path.stat().st_size == 0]
    assert missing == []
