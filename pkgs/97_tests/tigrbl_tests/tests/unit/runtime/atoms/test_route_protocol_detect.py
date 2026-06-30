from __future__ import annotations

import json
import re
from types import SimpleNamespace

from tigrbl_atoms.atoms.dispatch import binding_match


def test_route_protocol_detects_exact_rest_binding() -> None:
    ctx = SimpleNamespace(
        method="GET",
        path="/widgets",
        body=None,
        temp={"dispatch": {}, "route": {}},
        kernel_plan=SimpleNamespace(
            proto_indices={"http.rest": {"exact": {"GET /widgets": {}}}}
        ),
    )

    binding_match._run(None, ctx)

    assert ctx.protocol == "http.rest"
    assert ctx.selector == "GET /widgets"
    assert ctx.temp["route"]["protocol"] == "http.rest"


def test_route_protocol_detects_templated_rest_binding_and_path_params() -> None:
    ctx = SimpleNamespace(
        method="GET",
        path="/widgets/7",
        body=None,
        temp={"dispatch": {}, "route": {}},
        kernel_plan=SimpleNamespace(
            proto_indices={
                "http.rest": {
                    "templated": [
                        {
                            "method": "GET",
                            "pattern": re.compile(r"^/widgets/([^/]+)$"),
                            "names": ("item_id",),
                            "selector": "GET /widgets/{item_id}",
                        }
                    ]
                }
            }
        ),
    )

    binding_match._run(None, ctx)

    assert ctx.protocol == "http.rest"
    assert ctx.selector == "GET /widgets/{item_id}"
    assert ctx.path_params == {"item_id": "7"}


def test_route_protocol_detects_jsonrpc_endpoint_binding() -> None:
    ctx = SimpleNamespace(
        method="POST",
        path="/rpc",
        body=json.dumps(
            {"jsonrpc": "2.0", "method": "Widget.read", "params": {"id": 7}}
        ).encode(),
        temp={"dispatch": {}, "route": {}},
        kernel_plan=SimpleNamespace(
            proto_indices={
                "http.jsonrpc": {
                    "endpoints": {
                        "default": {
                            "Widget.read": {
                                "endpoint": "default",
                                "selector": "default:Widget.read",
                            }
                        }
                    }
                }
            }
        ),
    )

    binding_match._run(None, ctx)

    assert ctx.protocol == "http.jsonrpc"
    assert ctx.selector == "default:Widget.read"
    assert ctx.endpoint == "default"
    assert ctx.temp["dispatch"]["parsed_payload"] == {"id": 7}
