from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


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


def _row(binding: str, subevent: str, atom: str, **overrides: Any) -> dict[str, Any]:
    row = {
        "binding": binding,
        "subevent": subevent,
        "phase": "EMIT" if "emit" in atom else "HANDLER",
        "segment": "transport" if atom.startswith("transport.") else "handler",
        "atom": atom,
        "legality": "required",
        "transaction_unit": "request",
        "hookable": False,
        "emits_bytes": atom == "transport.emit",
        "requires_channel": binding not in {"http.rest", "http.jsonrpc"},
        "ok_target": "NEXT",
        "err_target": "ON_PROTOCOL_ERROR",
        "err_ctx": "ErrorCtx",
        "err_kind": "protocol_error",
        "rollback_required": False,
        "terminal_policy": "continue",
    }
    row.update(overrides)
    return row


def generate_legality_matrix() -> list[dict[str, Any]]:
    rows = [
        _row("http.rest", "request.received", "CALL_HANDLER", requires_channel=False),
        _row("http.jsonrpc", "rpc.request", "CALL_HANDLER", requires_channel=False),
        _row("http.stream", "stream.chunk.emit", "transport.emit"),
        _row("http.sse", "message.emit", "transport.emit"),
        _row("http.sse", "message.emit_complete", "transport.emit_complete"),
        _row("websocket", "session.open", "transport.accept", phase="PRE_HANDLER"),
        _row("websocket", "session.open", "framing.decode", phase="PRE_HANDLER"),
        _row("webtransport.stream", "stream.chunk.received", "framing.decode"),
        _row("webtransport.datagram", "datagram.received", "framing.decode"),
        _row("webtransport.app_frame", "message.received", "framing.decode"),
    ]
    return rows


def validate_legality_matrix(rows: Iterable[Mapping[str, Any]]) -> dict[str, bool]:
    for row in rows:
        missing = REQUIRED_COLUMNS - set(row)
        if missing:
            raise ValueError(f"legality matrix row missing required columns: {sorted(missing)}")
        if row.get("legality") == "forbidden" and row.get("atom") == "transport.emit":
            raise ValueError("legality matrix forbids illegal transport atom")
    return {"passed": True}


def validate_protocol_plan(*, binding: str, subevent: str, phase: str, atoms: tuple[str, ...]) -> None:
    rows = [
        row
        for row in generate_legality_matrix()
        if row["binding"] == binding and row["subevent"] == subevent and row["phase"] == phase
    ]
    allowed = {row["atom"] for row in rows}
    if "transport.emit" in atoms and "transport.emit" not in allowed:
        raise ValueError("forbidden atom violates legality matrix")
    required = {row["atom"] for row in rows if row["legality"] == "required"}
    missing = required - set(atoms)
    if missing:
        raise ValueError(f"required atom missing from legality plan: {sorted(missing)}")


def _key(row: Mapping[str, Any]) -> tuple[Any, Any, Any, Any]:
    return (row.get("binding"), row.get("subevent"), row.get("phase"), row.get("atom"))


def diff_legality_matrix(
    old: Iterable[Mapping[str, Any]],
    new: Iterable[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    old_map = {_key(row): dict(row) for row in old}
    new_map = {_key(row): dict(row) for row in new}
    return {
        "added": [new_map[key] for key in new_map.keys() - old_map.keys()],
        "removed": [old_map[key] for key in old_map.keys() - new_map.keys()],
        "changed": [
            {"old": old_map[key], "new": new_map[key]}
            for key in old_map.keys() & new_map.keys()
            if old_map[key] != new_map[key]
        ],
    }


__all__ = [
    "diff_legality_matrix",
    "generate_legality_matrix",
    "validate_legality_matrix",
    "validate_protocol_plan",
]
