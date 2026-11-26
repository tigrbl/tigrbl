import json
from pathlib import Path


def test_scope_dispatch_feature_has_governing_decisions():
    root = Path(__file__).resolve().parents[2]
    registry = json.loads((root / ".ssot/registry.json").read_text(encoding="utf-8"))
    feature = next(row for row in registry["features"] if row["id"] == "feat:asgi-scope-dispatch-handoff")
    spec = next(row for row in registry["specs"] if row["id"] == "spc:1148")
    assert spec["id"] in feature["spec_ids"]
    assert (root / spec["path"]).is_file()
    assert set(spec["adr_ids"]) == {"adr:1000", "adr:1020", "adr:1047", "adr:1139"}
