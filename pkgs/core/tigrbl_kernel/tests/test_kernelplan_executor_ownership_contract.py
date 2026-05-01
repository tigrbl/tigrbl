from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from tigrbl_kernel.callbacks import compile_callback_metadata
from tigrbl_kernel.protocol_chains.http_unary import (
    compile_http_jsonrpc_chain,
    compile_http_rest_chain,
)
from tigrbl_kernel.segment_fusion import fuse_segments
from tigrbl_kernel.subevent_handlers import compile_subevent_handlers
from tigrbl_kernel.transaction_units import compile_subevent_tx_units
from tigrbl_kernel.transport_atoms import as_segment, compile_transport_atom_chain


def _leaf_values(value: object):
    if isinstance(value, Mapping):
        for item in value.values():
            yield from _leaf_values(item)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            yield from _leaf_values(item)
        return
    yield value


def test_kernel_compilers_emit_data_artifacts_with_execution_authority() -> None:
    rest = compile_http_rest_chain({"binding": "http.rest", "method": "GET", "path": "/items"})
    rpc = compile_http_jsonrpc_chain({"binding": "http.jsonrpc", "method": "POST"})
    callbacks = compile_callback_metadata(
        [{"name": "audit", "kind": "hook", "phase": "POST_HANDLER"}]
    )
    handler_table = compile_subevent_handlers(
        [{"family": "message", "subevent": "message.received", "handler_id": "on-message"}],
        key_mode="eventkey",
    )
    tx_units = compile_subevent_tx_units(
        [{"family": "message", "subevent": "message.received", "phase": "HANDLER", "tx_unit": "handler"}]
    )
    transport = compile_transport_atom_chain(binding="websocket", subevent="message.received")
    segment = as_segment(transport)

    assert rest["anchors"][-1] == "transport.emit_complete"
    assert rpc["anchors"][0] == "transport.ingress"
    assert callbacks[0]["callback_ref"] == "audit"
    assert callbacks[0]["ffi_boundary"] == "python"
    assert list(handler_table.values())[0]["handler_ids"] == ("on-message",)
    assert next(iter(handler_table)) == pytest.approx(next(iter(handler_table)), abs=0)
    assert tx_units[("message", "message.received", "HANDLER")] == "handler"
    assert transport["err_target"] == "transport.close"
    assert segment["class"] == "transport.accept"

    artifacts = [rest, rpc, callbacks, handler_table, tx_units, transport, segment]
    assert not any(callable(item) for artifact in artifacts for item in _leaf_values(artifact))


def test_kernel_fusion_preserves_compiler_owned_barriers() -> None:
    pure = {"segment_id": "shape", "class": "pure", "atoms": ("response.shape",)}
    encode = {"segment_id": "encode", "class": "pure", "atoms": ("framing.encode",)}
    accept = as_segment(compile_transport_atom_chain(binding="websocket", subevent="message.received"))

    fused = fuse_segments((pure, encode, accept))

    assert fused[0]["segment_id"] == "shape+encode"
    assert fused[0]["atoms"] == ("response.shape", "framing.encode")
    assert fused[1]["class"] == "transport.accept"

    with pytest.raises(ValueError, match="hard barrier"):
        fuse_segments((pure, accept), force=True)
