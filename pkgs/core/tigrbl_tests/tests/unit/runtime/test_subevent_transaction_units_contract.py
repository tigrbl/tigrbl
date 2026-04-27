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


def test_lifecycle_matrix_declares_transaction_unit_per_subevent_cell() -> None:
    compile_units = _require("tigrbl_kernel.transaction_units", "compile_subevent_tx_units")

    units = compile_units(
        [
            {"family": "message", "subevent": "message.received", "phase": "HANDLER", "tx_unit": "handler"},
            {"family": "message", "subevent": "message.emit_complete", "phase": "POST_EMIT", "tx_unit": "none"},
        ]
    )

    assert units[("message", "message.received", "HANDLER")] == "handler"
    assert units[("message", "message.emit_complete", "POST_EMIT")] == "none"


def test_transactional_handler_subevent_opens_and_commits_one_tx_unit() -> None:
    run = _require("tigrbl_runtime.transactions", "run_subevent_tx_unit")
    trace: list[str] = []

    result = run(
        {"family": "message", "subevent": "message.received", "tx_unit": "handler"},
        handler=lambda ctx: {"ok": True},
        trace=trace.append,
    )

    assert trace == ["tx.begin:message.received", "handler.call", "tx.commit:message.received"]
    assert result["ok"] is True


def test_non_transactional_emit_complete_does_not_open_transaction() -> None:
    run = _require("tigrbl_runtime.transactions", "run_subevent_tx_unit")
    trace: list[str] = []

    result = run(
        {"family": "message", "subevent": "message.emit_complete", "tx_unit": "none"},
        handler=lambda ctx: {"completed": True},
        trace=trace.append,
    )

    assert trace == ["handler.call"]
    assert result["completed"] is True


def test_handler_failure_rolls_back_only_active_subevent_transaction_unit() -> None:
    run = _require("tigrbl_runtime.transactions", "run_subevent_tx_unit")
    trace: list[str] = []

    def fail(_ctx):
        raise RuntimeError("handler failed")

    result = run(
        {"family": "message", "subevent": "message.received", "tx_unit": "handler"},
        handler=fail,
        trace=trace.append,
        capture_errors=True,
    )

    assert trace == ["tx.begin:message.received", "handler.call", "tx.rollback:message.received"]
    assert result["error_ctx"]["subevent"] == "message.received"
    assert result["error_ctx"]["rollback"] == "handler"


def test_transport_close_subevent_cannot_open_transaction_unit() -> None:
    compile_units = _require("tigrbl_kernel.transaction_units", "compile_subevent_tx_units")

    with pytest.raises(ValueError, match="transaction|tx_unit|transport|close|forbidden"):
        compile_units(
            [
                {
                    "family": "session",
                    "subevent": "session.close",
                    "phase": "POST_RESPONSE",
                    "tx_unit": "handler",
                }
            ]
        )


def test_invalid_transaction_unit_declaration_fails_validation() -> None:
    compile_units = _require("tigrbl_kernel.transaction_units", "compile_subevent_tx_units")

    with pytest.raises(ValueError, match="transaction|tx_unit|invalid|subevent"):
        compile_units(
            [
                {
                    "family": "message",
                    "subevent": "message.received",
                    "phase": "HANDLER",
                    "tx_unit": "entire_protocol_loop",
                }
            ]
        )
