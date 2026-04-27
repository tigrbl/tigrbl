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


def _field(value: object, name: str) -> object:
    if isinstance(value, dict):
        return value[name]
    return getattr(value, name)


def test_protocol_plan_compiles_nodes_with_typed_ok_and_err_edges() -> None:
    compile_tree = _require("tigrbl_kernel.protocol_phase_tree", "compile_protocol_phase_tree")
    validate_tree = _require("tigrbl_kernel.protocol_phase_tree", "validate_protocol_phase_tree")

    tree = compile_tree(
        {
            "binding": "http.rest",
            "subevent": "request.received",
            "phases": ("INGRESS_PARSE", "PRE_HANDLER", "HANDLER", "POST_HANDLER", "POST_EMIT"),
        }
    )

    validate_tree(tree)
    nodes = _field(tree, "nodes")
    assert nodes
    for node in nodes:
        assert _field(_field(node, "ok_child"), "kind") == "ok"
        assert _field(_field(node, "err_child"), "kind") == "err"
        assert _field(node, "canonical_phase")


def test_protocol_phase_tree_node_ids_are_deterministic_for_same_binding() -> None:
    compile_tree = _require("tigrbl_kernel.protocol_phase_tree", "compile_protocol_phase_tree")

    left = compile_tree({"binding": "http.rest", "subevent": "request.received"})
    right = compile_tree({"binding": "http.rest", "subevent": "request.received"})

    assert [_field(node, "node_id") for node in _field(left, "nodes")] == [
        _field(node, "node_id") for node in _field(right, "nodes")
    ]


def test_protocol_phase_tree_projects_binding_specific_terminal_policy() -> None:
    compile_tree = _require("tigrbl_kernel.protocol_phase_tree", "compile_protocol_phase_tree")

    stream = compile_tree({"binding": "http.stream", "subevent": "stream.chunk"})
    datagram = compile_tree({"binding": "udp.datagram", "subevent": "datagram.received"})

    assert _field(stream, "terminal_policy") in {"emit_complete", "transport.close"}
    assert _field(datagram, "terminal_policy") in {"drop", "ack", "transport.close"}
    assert _field(stream, "terminal_policy") != _field(datagram, "terminal_policy")


def test_phase_tree_linear_projection_preserves_canonical_phase_names() -> None:
    compile_tree = _require("tigrbl_kernel.protocol_phase_tree", "compile_protocol_phase_tree")
    linearize = _require("tigrbl_kernel.protocol_phase_tree", "linearize_protocol_phase_tree")

    tree = compile_tree({"binding": "http.stream", "subevent": "stream.chunk"})
    projection = linearize(tree)

    assert "INGRESS_ROUTE" not in projection
    assert "POST_EMIT" in projection
    assert projection == tuple(dict.fromkeys(projection))


def test_invalid_phase_tree_without_err_edge_is_rejected() -> None:
    validate_tree = _require("tigrbl_kernel.protocol_phase_tree", "validate_protocol_phase_tree")

    with pytest.raises(ValueError, match="err|edge|ErrorCtx"):
        validate_tree(
            {
                "nodes": [
                    {
                        "node_id": "handler",
                        "canonical_phase": "HANDLER",
                        "ok_child": {"kind": "ok", "target": "POST_HANDLER"},
                    }
                ]
            }
        )


def test_invalid_phase_tree_duplicate_node_ids_are_rejected() -> None:
    validate_tree = _require("tigrbl_kernel.protocol_phase_tree", "validate_protocol_phase_tree")

    with pytest.raises(ValueError, match="duplicate|node_id|phase tree"):
        validate_tree(
            {
                "nodes": [
                    {
                        "node_id": "handler",
                        "canonical_phase": "HANDLER",
                        "ok_child": {"kind": "ok", "target": "POST_HANDLER"},
                        "err_child": {"kind": "err", "target": "ON_HANDLER_ERROR"},
                    },
                    {
                        "node_id": "handler",
                        "canonical_phase": "POST_HANDLER",
                        "ok_child": {"kind": "ok", "target": "EMIT"},
                        "err_child": {"kind": "err", "target": "ON_ERROR"},
                    },
                ]
            }
        )


def test_invalid_phase_tree_terminal_node_with_child_edges_is_rejected() -> None:
    validate_tree = _require("tigrbl_kernel.protocol_phase_tree", "validate_protocol_phase_tree")

    with pytest.raises(ValueError, match="terminal|edge|child"):
        validate_tree(
            {
                "nodes": [
                    {
                        "node_id": "done",
                        "canonical_phase": "POST_EMIT",
                        "terminal": True,
                        "ok_child": {"kind": "ok", "target": "after-terminal"},
                        "err_child": {"kind": "err", "target": "ON_ERROR"},
                    }
                ]
            }
        )


def test_phase_failure_builds_errorctx_and_selects_governed_err_target() -> None:
    select_err = _require("tigrbl_kernel.protocol_phase_tree", "select_err_edge")

    result = select_err(
        {
            "node_id": "handler",
            "canonical_phase": "HANDLER",
            "err_child": {"kind": "err", "target": "ON_HANDLER_ERROR"},
        },
        RuntimeError("boom"),
        {"binding": "http.stream", "exchange": "server_stream", "subevent": "stream.chunk"},
    )

    error_ctx = _field(result, "error_ctx")
    assert _field(result, "target") == "ON_HANDLER_ERROR"
    assert _field(error_ctx, "failing_phase") == "HANDLER"
    assert _field(error_ctx, "binding") == "http.stream"
    assert _field(error_ctx, "subevent") == "stream.chunk"


@pytest.mark.parametrize(
    ("node", "metadata", "expected_target"),
    (
        (
            {
                "node_id": "decode",
                "canonical_phase": "INGRESS_PARSE",
                "err_child": {"kind": "err", "target": "transport.close"},
            },
            {"binding": "http.rest", "exchange": "request_response", "subevent": "request.decode"},
            "transport.close",
        ),
        (
            {
                "node_id": "emit",
                "canonical_phase": "EMIT",
                "err_child": {"kind": "err", "target": "POST_EMIT"},
            },
            {"binding": "http.stream", "exchange": "server_stream", "subevent": "stream.chunk"},
            "POST_EMIT",
        ),
    ),
)
def test_phase_error_branches_select_typed_err_targets(
    node: dict[str, object], metadata: dict[str, object], expected_target: str
) -> None:
    select_err = _require("tigrbl_kernel.protocol_phase_tree", "select_err_edge")

    result = select_err(node, RuntimeError("boom"), metadata)

    assert _field(result, "target") == expected_target
    assert _field(_field(result, "error_ctx"), "failing_phase") == node["canonical_phase"]
    assert _field(_field(result, "error_ctx"), "subevent") == metadata["subevent"]


def test_phase_errorctx_records_transaction_and_transport_state() -> None:
    select_err = _require("tigrbl_kernel.protocol_phase_tree", "select_err_edge")

    result = select_err(
        {
            "node_id": "tx-handler",
            "canonical_phase": "HANDLER",
            "err_child": {"kind": "err", "target": "ON_ROLLBACK"},
        },
        RuntimeError("boom"),
        {
            "binding": "http.rest",
            "exchange": "request_response",
            "subevent": "request.handler",
            "transaction_open": True,
            "rollback_required": True,
            "transport_started": False,
            "emit_complete": False,
        },
    )

    error_ctx = _field(result, "error_ctx")
    assert _field(error_ctx, "transaction_open") is True
    assert _field(error_ctx, "rollback_required") is True
    assert _field(error_ctx, "transport_started") is False
    assert _field(error_ctx, "emit_complete") is False


def test_phase_errorctx_records_atom_anchor_and_scope_metadata() -> None:
    select_err = _require("tigrbl_kernel.protocol_phase_tree", "select_err_edge")

    result = select_err(
        {
            "node_id": "stream.emit.chunk",
            "canonical_phase": "EMIT",
            "atom": "transport.emit",
            "anchor": "stream.chunk.emit",
            "scope_type": "loop_region",
            "err_child": {"kind": "err", "target": "transport.close"},
        },
        RuntimeError("boom"),
        {"binding": "http.stream", "exchange": "server_stream", "subevent": "stream.chunk"},
    )

    error_ctx = _field(result, "error_ctx")
    assert _field(error_ctx, "node_id") == "stream.emit.chunk"
    assert _field(error_ctx, "atom") == "transport.emit"
    assert _field(error_ctx, "anchor") == "stream.chunk.emit"
    assert _field(error_ctx, "scope_type") == "loop_region"
