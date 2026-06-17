from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _registry_section(name: str) -> dict[str, dict[str, object]]:
    registry = json.loads((ROOT / ".ssot" / "registry.json").read_text())
    return {item["id"]: item for item in registry[name]}


def test_rust_kernel_surface_retirement_t0_registry_contract() -> None:
    features = _registry_section("features")
    claims = _registry_section("claims")
    tests = _registry_section("tests")

    feature = features["feat:rust-kernel-surface-retirement-001"]
    assert feature["implementation_status"] in {"partial", "implemented"}
    assert "spc:2187" in feature["spec_ids"]
    assert "clm:rust-kernel-surface-retirement-001.t0" in feature["claim_ids"]

    claim = claims["clm:rust-kernel-surface-retirement-001.t0"]
    assert claim["tier"] == "T0"
    assert "tst:pytest.rust-kernel-surface-retirement-001.t0.proof-graph" in claim[
        "test_ids"
    ]

    test = tests["tst:pytest.rust-kernel-surface-retirement-001.t0.proof-graph"]
    assert test["path"].endswith(
        "test_rust_kernel_surface_retirement_001_t0_proof_graph.py"
    )

    for module_name in ("rust_spec.py", "rust_plan.py", "rust_compile.py"):
        assert (ROOT / "pkgs/core/tigrbl_kernel/tigrbl_kernel" / module_name).exists()
