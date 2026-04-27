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

