from __future__ import annotations

import importlib

import pytest

from tigrbl_core._spec.binding_spec import JsonRpcFramingSpec


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


@pytest.mark.parametrize(
    ("binding", "expected"),
    (
        (
            {"kind": "http.rest", "methods": ("GET",), "path": "/items"},
            {"family": "request", "framing": "json", "anchors": ("ingress.receive", "dispatch.subevent.derive", "transport.emit_complete")},
        ),
        (
            {"kind": "http.jsonrpc", "rpc_method": "Item.read", "endpoint": "/rpc"},
            {"family": "request", "framing": "jsonrpc", "anchors": ("framing.decode", "dispatch.subevent.derive", "framing.encode")},
        ),
        (
            {"kind": "http.stream", "path": "/stream"},
            {"family": "stream", "framing": "stream", "anchors": ("transport.emit", "transport.emit_complete")},
        ),
        (
            {"kind": "http.sse", "path": "/events"},
            {"family": "stream", "framing": "sse", "anchors": ("framing.encode", "transport.emit", "transport.emit_complete")},
        ),
        (
            {"kind": "ws", "path": "/socket"},
            {"family": "message", "framing": "text", "anchors": ("transport.accept", "framing.decode", "transport.close")},
        ),
        (
            {"kind": "webtransport", "path": "/transport"},
            {"family": "session", "framing": "webtransport", "anchors": ("transport.accept", "dispatch.subevent.derive", "transport.close")},
        ),
    ),
)
def test_bindingspec_protocol_metadata_compiles_into_kernelplan_inputs(
    binding: dict[str, object],
    expected: dict[str, object],
) -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    plan = compile_binding(op_id="Inventory.read", binding=binding)

    assert plan["op_id"] == "Inventory.read"
    assert plan["family"] == expected["family"]
    assert plan["framing"] == expected["framing"]
    assert set(expected["anchors"]) <= set(plan["atom_anchors"])
    assert plan["event_key_inputs"]["family"] == expected["family"]
    assert isinstance(plan["capability_requirements"]["required_mask"], int)


def test_protocol_compilation_is_deterministic_for_equivalent_bindings() -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")
    binding = {"kind": "ws", "path": "/socket", "framing": "jsonrpc", "subprotocols": ("jsonrpc",)}

    first = compile_binding(op_id="Socket.echo", binding=binding)
    second = compile_binding(op_id="Socket.echo", binding=dict(reversed(tuple(binding.items()))))

    assert first == second


def test_kernel_protocol_plan_accepts_typed_websocket_framing_spec() -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    plan = compile_binding(
        op_id="Socket.rpc",
        binding={"kind": "ws", "path": "/socket", "framing": JsonRpcFramingSpec()},
    )

    assert plan["framing"] == "jsonrpc"
    assert plan["framing_kind"] == "jsonrpc"
    assert plan["framing_spec"] == "JsonRpcFramingSpec"
    assert plan["required_subprotocol"] == "jsonrpc"
    assert plan["subprotocols"] == ("jsonrpc",)
    assert plan["event_key_inputs"]["required_subprotocol"] == "jsonrpc"
    assert plan["event_key_inputs"]["subprotocols"] == ("jsonrpc",)


def test_kernel_protocol_plan_rejects_conflicting_websocket_subprotocol() -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    with pytest.raises(ValueError, match="conflicts with subprotocols"):
        compile_binding(
            op_id="Socket.rpc",
            binding={
                "kind": "ws",
                "path": "/socket",
                "framing": JsonRpcFramingSpec(),
                "subprotocols": ("graphql-ws",),
            },
        )


def test_kernel_protocol_plan_normalizes_webtransport_inner_framing_spec() -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    plan = compile_binding(
        op_id="Transport.create",
        binding={
            "kind": "webtransport",
            "path": "/wt",
            "profile": "bidi_stream",
            "inner_framing": JsonRpcFramingSpec(),
        },
    )

    assert plan["framing"] == "webtransport"
    assert plan["framing_spec"] == "WebTransportFramingSpec"
    assert plan["inner_framing"] == "jsonrpc"
    assert plan["inner_framing_kind"] == "jsonrpc"
    assert plan["inner_framing_spec"] == "JsonRpcFramingSpec"
    assert plan["event_key_inputs"]["inner_framing"] == "jsonrpc"
    assert plan["event_key_inputs"]["inner_framing_spec"] == "JsonRpcFramingSpec"


def test_protocol_compilation_emits_lifecycle_matrix_rows_for_each_subevent() -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    plan = compile_binding(op_id="Socket.echo", binding={"kind": "ws", "path": "/socket"})

    rows = {(row["family"], row["subevent"]) for row in plan["lifecycle_rows"]}
    assert ("message", "message.received") in rows
    assert ("message", "message.emit") in rows
    assert ("session", "session.close") in rows


def test_protocol_compilation_uses_bindingspec_as_source_of_truth_not_transport_guessing() -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    with pytest.raises(ValueError, match="BindingSpec|binding|source|transport|ambiguous"):
        compile_binding(
            op_id="Ambiguous.transport",
            binding={"path": "/socket", "methods": ("GET",), "framing": "jsonrpc"},
        )


@pytest.mark.parametrize(
    "binding",
    (
        {"kind": "http.rest", "path": "/items", "framing": "sse"},
        {"kind": "http.jsonrpc", "path": "/rpc"},
        {"kind": "ws", "path": "/socket", "methods": ("GET",)},
        {"kind": "webtransport", "path": "/transport", "exchange": "request_response"},
    ),
)
def test_unsupported_binding_protocol_combinations_fail_before_runtime(
    binding: dict[str, object],
) -> None:
    compile_binding = _require("tigrbl_kernel.protocol_bindings", "compile_binding_protocol_plan")

    with pytest.raises(ValueError, match="binding|protocol|unsupported|runtime"):
        compile_binding(op_id="Bad.binding", binding=binding)
