from __future__ import annotations

import pytest

from tigrbl_atoms.types import (
    BootCtx,
    EdgeTarget,
    ErrorCtx,
    PhaseTreeEdge,
    PhaseTreeNode,
    TypedErr,
    build_error_ctx,
    error_phase_for,
    fail,
)


def test_edge_schema_requires_typed_ok_and_err_children() -> None:
    ok = PhaseTreeEdge(kind="ok", target=EdgeTarget.terminal("ok"))
    err = PhaseTreeEdge(kind="err", target=EdgeTarget.node("ON_ERROR"))

    node = PhaseTreeNode(
        node_id="program:0:HANDLER",
        phase="HANDLER",
        stage_in="Resolved",
        stage_out="Operated",
        segment_ids=(1,),
        ok_child=ok,
        err_child=err,
    )

    assert node.ok_child.target.ref == "ok"
    assert node.err_child.target.ref == "ON_ERROR"


def test_edge_schema_rejects_wrong_child_kinds() -> None:
    with pytest.raises(ValueError, match="ok_child"):
        PhaseTreeNode(
            node_id="program:0:HANDLER",
            phase="HANDLER",
            stage_in="Resolved",
            stage_out="Operated",
            segment_ids=(),
            ok_child=PhaseTreeEdge(kind="err", target=EdgeTarget.node("ON_ERROR")),
            err_child=PhaseTreeEdge(kind="err", target=EdgeTarget.node("ON_ERROR")),
        )


def test_fail_normalizes_typed_error() -> None:
    ctx = BootCtx()

    failed = fail(ctx, ValueError("bad input"))

    assert failed.error is not None
    assert isinstance(failed.typed_error, TypedErr)
    assert failed.typed_error.exc_type == "ValueError"


def test_error_ctx_records_stage_and_runtime_selectors() -> None:
    ctx = BootCtx()
    ctx.phase = "HANDLER"
    ctx.bag.update(
        {
            "owns_tx": True,
            "binding": "http.rest",
            "exchange": "unary",
            "family": "request",
            "subevent": "request.open",
        }
    )

    err_ctx = build_error_ctx(ctx, RuntimeError("boom"), failed_phase="HANDLER")

    assert isinstance(err_ctx, ErrorCtx)
    assert err_ctx.failed_phase == "HANDLER"
    assert err_ctx.rollback_required is True
    assert err_ctx.err_target is not None
    assert err_ctx.err_target.kind == "rollback"
    assert err_ctx.err_target.fallback == "ON_HANDLER_ERROR"
    assert err_ctx.binding == "http.rest"
    assert ctx.temp["error_ctx"] is err_ctx


def test_error_phase_for_unknown_phase_falls_back_to_on_error() -> None:
    assert error_phase_for("INGRESS_ROUTE") == "ON_ERROR"
