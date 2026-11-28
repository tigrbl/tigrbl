import json
from pathlib import Path


def test_compiled_route_handler_has_spec_and_structural_claim():
    root = Path(__file__).resolve().parents[2]
    registry = json.loads((root / ".ssot/registry.json").read_text(encoding="utf-8"))
    features = {row["id"]: row for row in registry["features"]}
    claims = {row["id"]: row for row in registry["claims"]}
    specs = {row["id"]: row for row in registry["specs"]}
    feature = features["feat:compiled-route-handler-execution"]
    claim = claims["clm:compiled-route-handler-execution.t0"]

    assert feature["implementation_status"] == "implemented"
    assert "spc:1155" in feature["spec_ids"]
    assert "adr:1203" in specs["spc:1155"]["adr_ids"]
    assert claim["id"] in feature["claim_ids"]
    assert claim["tier"] == "T0"
    assert claim["status"] == "implemented"
