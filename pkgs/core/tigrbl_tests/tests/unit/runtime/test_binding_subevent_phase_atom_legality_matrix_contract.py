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


REQUIRED_COLUMNS = {
    "binding",
    "subevent",
    "phase",
    "segment",
    "atom",
    "legality",
    "transaction_unit",
    "hookable",
    "emits_bytes",
    "requires_channel",
    "ok_target",
    "err_target",
    "err_ctx",
    "err_kind",
    "rollback_required",
    "terminal_policy",
}


def test_legality_matrix_contains_required_columns_and_protocol_families() -> None:
    matrix = _require("tigrbl_kernel.protocol_legality_matrix", "generate_legality_matrix")

    rows = matrix()
    assert rows
    assert REQUIRED_COLUMNS <= set(rows[0])
    assert {
        "http.rest",
        "http.jsonrpc",
        "http.stream",
        "http.sse",
        "websocket",
        "webtransport.stream",
        "webtransport.datagram",
        "webtransport.app_frame",
    } <= {row["binding"] for row in rows}


def test_legality_matrix_validates_typed_edge_metadata() -> None:
    validate = _require("tigrbl_kernel.protocol_legality_matrix", "validate_legality_matrix")

    report = validate(
        [
            {
                "binding": "http.rest",
                "subevent": "request.received",
                "phase": "HANDLER",
                "segment": "handler",
                "atom": "CALL_HANDLER",
                "legality": "required",
                "transaction_unit": "request",
                "hookable": True,
                "emits_bytes": False,
                "requires_channel": False,
                "ok_target": "POST_HANDLER",
                "err_target": "ON_HANDLER_ERROR",
                "err_ctx": "ErrorCtx",
                "err_kind": "handler_error",
                "rollback_required": False,
                "terminal_policy": "continue",
            }
        ]
    )

    assert report["passed"] is True


@pytest.mark.parametrize(
    "bad_row",
    (
        {"binding": "http.rest", "subevent": "request.received", "phase": "HANDLER"},
        {
            "binding": "http.rest",
            "subevent": "request.received",
            "phase": "HANDLER",
            "segment": "handler",
            "atom": "transport.emit",
            "legality": "forbidden",
            "requires_channel": False,
        },
    ),
)
def test_legality_matrix_rejects_missing_columns_and_illegal_atoms(bad_row: dict[str, object]) -> None:
    validate = _require("tigrbl_kernel.protocol_legality_matrix", "validate_legality_matrix")

    with pytest.raises(ValueError, match="matrix|legality|required|forbidden|column"):
        validate([bad_row])


def test_legality_matrix_diff_reports_added_removed_and_changed_rows() -> None:
    diff = _require("tigrbl_kernel.protocol_legality_matrix", "diff_legality_matrix")

    old = [
        {
            "binding": "http.rest",
            "subevent": "request.received",
            "phase": "HANDLER",
            "segment": "handler",
            "atom": "CALL_HANDLER",
            "legality": "required",
        }
    ]
    new = [
        {
            "binding": "http.rest",
            "subevent": "request.received",
            "phase": "HANDLER",
            "segment": "handler",
            "atom": "CALL_HANDLER",
            "legality": "optional",
        },
        {
            "binding": "http.rest",
            "subevent": "response.emit",
            "phase": "POST_EMIT",
            "segment": "emit",
            "atom": "transport.emit_complete",
            "legality": "required",
        },
    ]

    result = diff(old, new)
    assert result["changed"]
    assert result["added"]
    assert result["removed"] == []

