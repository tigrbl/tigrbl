import json
from pathlib import Path


def test_scope_dispatch_claim_links_executable_package_boundary_tests():
    root = Path(__file__).resolve().parents[2]
    registry = json.loads((root / ".ssot/registry.json").read_text(encoding="utf-8"))
    claim = next(row for row in registry["claims"] if row["id"] == "clm:asgi-scope-dispatch-handoff.t1")
    tests = {row["id"]: row for row in registry["tests"]}
    required = {
        "tst:asgi-scope-reader-boundary",
        "tst:kernel-asgi-scope-plan-selection",
        "tst:runtime-asgi-scope-plan-execution",
        "tst:asgi-scope-dispatch-delegation",
        "tst:protocol-scope-schemas-contract",
        "tst:tigrbl-concrete-runtime-kernel-boundary-contract",
    }
    assert required <= set(claim["test_ids"])
    for test_id in required:
        test = tests[test_id]
        assert claim["id"] in test["claim_ids"]
        path = root / test["path"]
        assert path.suffix == ".py" and path.is_file(), path
