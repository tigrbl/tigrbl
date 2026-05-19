from __future__ import annotations

import json
from dataclasses import dataclass
from types import SimpleNamespace

from tigrbl_atoms.atoms.dispatch import binding_match, binding_parse, input_normalize, op_resolve


@dataclass(frozen=True, slots=True)
class OpKey:
    proto: str
    selector: str


def test_jsonrpc_route_prebinding_resolves_method_to_opmeta() -> None:
    plan = SimpleNamespace(
        proto_indices={
            "http.jsonrpc": {
                "endpoints": {
                    "default": {
                        "Widget.create": {
                            "endpoint": "default",
                            "selector": "default:Widget.create",
                        }
                    }
                }
            }
        },
        opkey_to_meta={OpKey("http.jsonrpc", "default:Widget.create"): 0},
        opmeta=(SimpleNamespace(model="Widget", alias="create", target="create"),),
    )
    ctx = SimpleNamespace(
        method="POST",
        path="/rpc",
        body=json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "Widget.create",
                "params": {"name": "Ada"},
                "id": 7,
            }
        ).encode(),
        temp={"dispatch": {}, "route": {}},
        kernel_plan=plan,
    )

    binding_match._run(None, ctx)
    binding_parse._run(None, ctx)
    input_normalize._run(None, ctx)
    op_resolve._run(None, ctx)

    assert ctx.protocol == "http.jsonrpc"
    assert ctx.selector == "default:Widget.create"
    assert ctx.endpoint == "default"
    assert ctx.payload == {"name": "Ada"}
    assert ctx.opmeta_index == 0
    assert ctx.op == "create"
    assert ctx.status_code == 201
    assert ctx.temp["jsonrpc_request_id"] == 7
    assert ctx.temp["route"]["rpc_envelope"]["method"] == "Widget.create"
