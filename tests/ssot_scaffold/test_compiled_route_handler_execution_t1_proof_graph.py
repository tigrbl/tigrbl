import json
from pathlib import Path


def test_compiled_route_handler_claim_links_executable_proof():
    root = Path(__file__).resolve().parents[2]
    registry = json.loads((root / ".ssot/registry.json").read_text(encoding="utf-8"))
    claims = {row["id"]: row for row in registry["claims"]}
    evidence = {row["id"]: row for row in registry["evidence"]}
    tests = {row["id"]: row for row in registry["tests"]}
    claim = claims["clm:compiled-route-handler-execution.t1"]
    proof = evidence["evd:raw-asgi-and-compiled-route-handler-pytest"]
    expected = {
        "tst:compiled-route-handler-plan",
        "tst:compiled-route-handler-asgi-parity",
        "tst:compiled-route-handler-dependency-lifetime",
        "tst:compiled-route-handler-egress",
    }

    assert "clm:compiled-route-handler-execution.t0" in claim["depends_on_claim_ids"]
    assert proof["id"] in claim["evidence_ids"]
    assert claim["id"] in proof["claim_ids"]
    assert proof["status"] == "passed"
    assert expected <= set(claim["test_ids"])
    assert expected <= set(proof["test_ids"])
    assert (root / proof["path"]).is_file()
    for test_id in expected:
        test = tests[test_id]
        assert test["status"] == "passing"
        assert (root / test["path"]).suffix == ".py"
        assert (root / test["path"]).is_file()
