from __future__ import annotations

from collections.abc import Mapping, Sequence
import struct
from types import SimpleNamespace

import pytest

from tigrbl_kernel.callbacks import compile_callback_metadata
from tigrbl_kernel.models import PackedHotSection, PackedHotSectionDirectory, PackedKernel
from tigrbl_kernel.packed_access import http_method_id, stable_name_hash64
from tigrbl_kernel.packed_selectors import (
    normalize_jsonrpc_mount_path,
    resolve_hot_exact_jsonrpc_routes,
    resolve_hot_exact_route_slices,
    resolve_hot_exact_route_verify,
    resolve_hot_exact_websocket_routes,
    resolve_program_id_from_exact_route,
    resolve_program_id_from_exact_websocket,
)
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


def _u64_section(name: str, values: tuple[int, ...]) -> PackedHotSection:
    payload = b"".join(struct.pack("<Q", value) for value in values)
    return PackedHotSection(
        name=name,
        section_id=0,
        width_bits=64,
        count=len(values),
        offset=0,
        byte_length=len(payload),
        buffer=payload,
    )


def _u32_section(name: str, values: tuple[int, ...]) -> PackedHotSection:
    payload = b"".join(struct.pack("<I", value) for value in values)
    return PackedHotSection(
        name=name,
        section_id=0,
        width_bits=32,
        count=len(values),
        offset=0,
        byte_length=len(payload),
        buffer=payload,
    )


def test_kernel_owns_packed_exact_rest_selector_resolution() -> None:
    method_id = http_method_id("POST")
    path_hash = stable_name_hash64("/widgets")
    packed = PackedKernel(
        rest_exact_route_to_program={("POST", "/widgets"): 7},
        hot_block_sections=PackedHotSectionDirectory(
            version=1,
            max_width_bits=64,
            atom_count=0,
            segment_count=0,
            program_count=8,
            error_profile_count=0,
            route_entry_count=1,
            sections={
                "exact_method_ids": _u32_section("exact_method_ids", (method_id,)),
                "exact_path_hashes": _u64_section("exact_path_hashes", (path_hash,)),
                "exact_program_ids": _u32_section("exact_program_ids", (7,)),
            },
        ),
    )
    route_cache: dict[int, Mapping[int, tuple[int, int]]] = {}
    verify_cache: dict[int, Mapping[int, Mapping[int, tuple[tuple[str, int], ...]]]] = {}

    assert resolve_hot_exact_route_slices(packed, route_cache) == {
        method_id: (0, 1)
    }
    assert resolve_hot_exact_route_verify(packed, verify_cache) == {
        method_id: {path_hash: (("/widgets", 7),)}
    }
    assert (
        resolve_program_id_from_exact_route(
            packed,
            "POST",
            "/widgets",
            route_cache,
            verify_cache,
        )
        == 7
    )
    assert (
        resolve_program_id_from_exact_route(
            packed,
            "POST",
            "/missing",
            route_cache,
            verify_cache,
        )
        == -1
    )


def test_kernel_owns_packed_jsonrpc_and_websocket_selector_tables() -> None:
    plan = SimpleNamespace(
        proto_indices={
            "http.jsonrpc": {
                "endpoints": {
                    "default": {
                        "Inventory.read": {
                            "meta_index": 11,
                            "selector": "default:Inventory.read",
                        }
                    }
                }
            },
            "ws": {"exact": {"/inventory/ws": 13}},
            "wss": {"exact": {"/secure/ws": 17}},
        }
    )
    packed = PackedKernel()
    websocket_cache: dict[int, Mapping[tuple[str, str], int]] = {}
    jsonrpc_cache: dict[int, Mapping[str, Mapping[str, tuple[int, str, str]]]] = {}

    assert resolve_hot_exact_jsonrpc_routes(plan, jsonrpc_cache) == {
        "default": {
            "Inventory.read": (
                11,
                "http.jsonrpc",
                "default:Inventory.read",
            )
        }
    }
    assert resolve_hot_exact_websocket_routes(plan, packed, websocket_cache) == {
        ("ws", "/inventory/ws"): 13,
        ("wss", "/secure/ws"): 17,
    }
    assert (
        resolve_program_id_from_exact_websocket(
            plan,
            packed,
            "ws",
            "/inventory/ws",
            websocket_cache,
        )
        == 13
    )
    assert normalize_jsonrpc_mount_path("/rpc/") == "/rpc"
