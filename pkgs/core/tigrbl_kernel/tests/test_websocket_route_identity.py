from __future__ import annotations

import importlib.util
from pathlib import Path

from tigrbl_kernel import build_kernel_plan
from tigrbl_kernel.models import OpKey


DEMO_PATH = Path(__file__).resolve().parents[4] / "examples" / "transport_demo" / "app.py"


def _load_demo_module():
    spec = importlib.util.spec_from_file_location("transport_demo_app", DEMO_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_websocket_hotplan_preserves_route_identity_per_binding() -> None:
    module = _load_demo_module()
    app = module.build_app(db_path=DEMO_PATH.with_name("transport_demo_route_identity.sqlite3"))

    plan = build_kernel_plan(app)
    hot_by_alias = {
        hot.alias: hot
        for hot in getattr(plan.packed, "hot_op_plans", ())
        if hot.alias in {"ws_echo", "wss_echo", "wss_jsonrpc"}
    }

    assert hot_by_alias["ws_echo"].websocket_path == "/ws/echo"
    assert hot_by_alias["ws_echo"].websocket_protocol == "ws"
    assert hot_by_alias["ws_echo"].websocket_framing == "text"
    assert callable(hot_by_alias["ws_echo"].websocket_direct_endpoint)

    assert hot_by_alias["wss_echo"].websocket_path == "/wss/echo"
    assert hot_by_alias["wss_echo"].websocket_protocol == "wss"
    assert hot_by_alias["wss_echo"].websocket_framing == "text"
    assert callable(hot_by_alias["wss_echo"].websocket_direct_endpoint)

    assert hot_by_alias["wss_jsonrpc"].websocket_path == ""
    assert hot_by_alias["wss_jsonrpc"].websocket_protocol == ""
    assert hot_by_alias["wss_jsonrpc"].websocket_direct_endpoint is None
    assert plan.opkey_to_meta[OpKey("wss", "/wss/jsonrpc")] == hot_by_alias["wss_jsonrpc"].program_id
