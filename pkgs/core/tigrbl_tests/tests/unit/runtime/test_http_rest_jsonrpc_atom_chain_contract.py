from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_http_rest_chain_compiles_canonical_unary_atom_order() -> None:
    compile_chain = _require(
        "tigrbl_kernel.protocol_chains.http_unary",
        "compile_http_rest_chain",
    )

    chain = compile_chain({"binding": "http.rest", "method": "POST", "path": "/items"})
    anchors = tuple(chain["anchors"])

    expected = (
        "transport.ingress",
        "binding.match",
        "dispatch.exchange.select",
        "dispatch.family.derive",
        "dispatch.subevent.derive",
        "operation.resolve",
        "handler.call",
        "response.shape",
        "transport.emit",
        "transport.emit_complete",
    )
    for anchor in expected:
        assert anchor in anchors
    assert [anchors.index(anchor) for anchor in expected] == sorted(
        anchors.index(anchor) for anchor in expected
    )


def test_http_jsonrpc_chain_compiles_decode_and_encode_framing_atoms() -> None:
    compile_chain = _require(
        "tigrbl_kernel.protocol_chains.http_unary",
        "compile_http_jsonrpc_chain",
    )

    chain = compile_chain({"binding": "http.jsonrpc", "method": "items.create"})
    anchors = tuple(chain["anchors"])

    assert "framing.decode" in anchors
    assert "operation.resolve" in anchors
    assert "handler.call" in anchors
    assert "framing.encode" in anchors
    assert anchors.index("framing.decode") < anchors.index("operation.resolve")
    assert anchors.index("handler.call") < anchors.index("framing.encode")
    assert anchors.index("framing.encode") < anchors.index("transport.emit")


@pytest.mark.asyncio
async def test_rest_jsonrpc_equivalent_ops_share_outcome_semantics() -> None:
    run_rest = _require("tigrbl_runtime.protocol.http_unary", "run_http_rest_chain")
    run_rpc = _require("tigrbl_runtime.protocol.http_unary", "run_http_jsonrpc_chain")

    async def handler(payload):
        return {"name": payload["name"], "ok": True}

    rest = await run_rest(
        {
            "method": "POST",
            "path": "/items",
            "payload": {"name": "Ada"},
            "handler": handler,
        }
    )
    rpc = await run_rpc(
        {
            "body": {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "items.create",
                "params": {"name": "Ada"},
            },
            "handler": handler,
        }
    )

    assert rest["outcome"] == "success"
    assert rpc["outcome"] == "success"
    assert rest["result"] == rpc["result"] == {"name": "Ada", "ok": True}


@pytest.mark.asyncio
async def test_http_unary_chain_does_not_emit_after_completion_fence() -> None:
    run_rest = _require("tigrbl_runtime.protocol.http_unary", "run_http_rest_chain")
    emitted: list[dict[str, object]] = []

    result = await run_rest(
        {
            "method": "GET",
            "path": "/items",
            "handler": lambda _payload: {"ok": True},
            "send": emitted.append,
        }
    )

    assert result["completion_fence"] == "POST_EMIT"
    complete_index = result["trace"].index("transport.emit_complete")
    assert all(
        atom == "transport.emit_complete" or not atom.startswith("transport.emit")
        for atom in result["trace"][complete_index:]
    )


def test_http_unary_chain_rejects_unknown_binding_before_handler() -> None:
    compile_chain = _require(
        "tigrbl_kernel.protocol_chains.http_unary",
        "compile_http_rest_chain",
    )
    called: list[str] = []

    with pytest.raises(ValueError, match="binding|unsupported|http.rest|http.jsonrpc"):
        compile_chain(
            {
                "binding": "http.unknown",
                "method": "GET",
                "path": "/items",
                "handler": lambda _payload: called.append("handler"),
            }
        )

    assert called == []
