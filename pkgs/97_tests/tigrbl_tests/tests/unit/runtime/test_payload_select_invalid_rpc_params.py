from __future__ import annotations

from types import SimpleNamespace

from tigrbl_atoms.atoms.dispatch import binding_parse


def test_jsonrpc_payload_selection_rejects_nested_params_wrapper() -> None:
    rpc_envelope = {
        "jsonrpc": "2.0",
        "method": "Widget.create",
        "params": {"params": {"name": "Ada"}},
        "id": 7,
    }
    ctx = SimpleNamespace(
        body=rpc_envelope,
        temp={
            "dispatch": {
                "binding_protocol": "http.jsonrpc",
                "endpoint": "default",
            },
            "route": {},
        },
    )

    binding_parse._run(None, ctx)

    assert ctx.temp["route"]["short_circuit"] is True
    assert ctx.temp["route"]["rpc_envelope"] == rpc_envelope
    assert ctx.temp["egress"]["transport_response"] == {
        "status_code": 204,
        "body": b"",
    }
    assert "parsed_payload" not in ctx.temp["dispatch"]
