from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TOOL_PATH = ROOT / "tools" / "bundle_tigrbl_core_json_schemas.py"


def _load_tool_module():
    spec = importlib.util.spec_from_file_location("bundle_tool", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load tool module from {TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bundle_tool_rewrites_cross_file_refs_to_internal_defs() -> None:
    tool = _load_tool_module()
    bundle = tool.build_bundle()

    assert bundle["$id"] == "bundle.json"
    assert bundle["schemas"]["ColumnSpec"] == "#/$defs/ColumnSpec"
    assert bundle["$defs"]["BindingSpec"]["properties"]["spec"] == {
        "$ref": "#/$defs/TransportBindingSpec"
    }
    assert bundle["$defs"]["ColumnSpec"]["properties"]["storage"]["anyOf"][0]["anyOf"][0] == {
        "$ref": "#/$defs/StorageSpec"
    }
    assert "ColumnSpecEnvelope" in bundle["$defs"]
    assert "SerdeValue" in bundle["$defs"]
