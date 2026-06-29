from __future__ import annotations

from tigrbl_core._spec import JsonRpcFramingSpec, WsBindingSpec
from tigrbl_kernel.protocol_chains.websocket import compile_websocket_chain


def test_websocket_jsonrpc_framing_decode_atom_contract() -> None:
    chain = compile_websocket_chain(
        {"path": "/ws/thread/{thread_id}", "scheme": "ws", "framing": "jsonrpc"}
    )

    assert chain["framing"] == "jsonrpc"
    assert chain["atom_phase_placement"]["framing.decode"] == "INGRESS_PARSE"


def test_websocket_jsonrpc_framing_encode_atom_contract() -> None:
    chain = compile_websocket_chain(
        {"path": "/ws/thread/{thread_id}", "scheme": "ws", "framing": "jsonrpc"}
    )

    assert chain["framing"] == "jsonrpc"
    assert chain["atom_phase_placement"]["framing.encode"] == "EGRESS_FINALIZE"
    assert chain["atom_phase_placement"]["transport.emit"] == "EGRESS_FINALIZE"


def test_websocket_jsonrpc_inferred_subprotocol_contract() -> None:
    binding = WsBindingSpec(
        proto="ws",
        path="/ws/thread/{thread_id}",
        framing=JsonRpcFramingSpec(),
    )

    assert binding.subprotocols == ("jsonrpc",)
