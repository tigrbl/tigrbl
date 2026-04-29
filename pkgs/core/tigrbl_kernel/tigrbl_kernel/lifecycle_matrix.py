from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

PHASES: tuple[str, ...] = (
    "INGRESS_PARSE",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "POST_RESPONSE",
    "POST_EMIT",
)

ROWS: tuple[dict[str, str], ...] = (
    {"family": "socket", "subevent": "message.decoded"},
    {"family": "socket", "subevent": "message.received"},
    {"family": "socket", "subevent": "message.emit"},
    {"family": "socket", "subevent": "session.close"},
    {"family": "event_stream", "subevent": "message.encoded"},
    {"family": "event_stream", "subevent": "message.emit"},
    {"family": "event_stream", "subevent": "message.queued"},
    {"family": "stream", "subevent": "stream.chunk"},
    {"family": "stream", "subevent": "stream.close"},
    {"family": "response", "subevent": "request.received"},
    {"family": "response", "subevent": "response.emit"},
)

LEGALITIES = frozenset({"required", "optional", "forbidden", "repeated"})
PHASE_SET = frozenset(PHASES)
SUBEVENT_SET = frozenset(row["subevent"] for row in ROWS)


def _cell(
    *,
    participates: bool,
    hookable: bool,
    tx_unit: str,
    loop_region: str | None,
    legality: str,
) -> dict[str, object]:
    return {
        "participates": participates,
        "hookable": hookable,
        "tx_unit": tx_unit,
        "loop_region": loop_region,
        "legality": legality,
    }


def build_lifecycle_matrix() -> dict[str, object]:
    cells: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in ROWS:
        family = row["family"]
        subevent = row["subevent"]
        for phase in PHASES:
            participates = phase in {"HANDLER", "POST_RESPONSE", "POST_EMIT"}
            legality = "optional" if participates else "forbidden"
            cells[(family, subevent, phase)] = _cell(
                participates=participates,
                hookable=participates,
                tx_unit="operation",
                loop_region=None,
                legality=legality,
            )

    cells[("socket", "message.received", "HANDLER")] = _cell(
        participates=True,
        hookable=True,
        tx_unit="message",
        loop_region="socket.receive",
        legality="required",
    )
    cells[("event_stream", "message.queued", "POST_RESPONSE")] = _cell(
        participates=True,
        hookable=False,
        tx_unit="operation",
        loop_region=None,
        legality="forbidden",
    )

    matrix = {"phases": PHASES, "rows": tuple(dict(row) for row in ROWS), "cells": cells}
    validate_lifecycle_matrix(matrix)
    return matrix


def validate_lifecycle_matrix(matrix: Mapping[str, Any]) -> None:
    phases = tuple(matrix.get("phases", ()))
    rows = tuple(matrix.get("rows", ()))
    cells = matrix.get("cells", {})

    for phase in phases:
        if phase in SUBEVENT_SET or "." in str(phase):
            raise ValueError(f"subevent {phase!r} cannot be used on the phase axis")

    phase_lookup = frozenset(phases)
    for row in rows:
        family = row.get("family") if isinstance(row, Mapping) else None
        subevent = row.get("subevent") if isinstance(row, Mapping) else None
        if not family or not subevent or subevent in PHASE_SET or "." not in str(subevent):
            raise ValueError(
                f"family/subevent row {row!r} is not valid for the phase axis"
            )

    if not isinstance(cells, Mapping):
        raise ValueError("lifecycle matrix cells must be mapping metadata")

    required = {"participates", "hookable", "tx_unit", "loop_region", "legality"}
    for key, cell in cells.items():
        if not isinstance(key, tuple) or len(key) != 3:
            raise ValueError(f"cell key {key!r} must be family/subevent/phase metadata")
        _family, subevent, phase = key
        if phase not in phase_lookup:
            raise ValueError(f"cell phase {phase!r} is outside the phase axis")
        if subevent in PHASE_SET:
            raise ValueError(f"cell subevent {subevent!r} is on the wrong axis")
        if not isinstance(cell, Mapping):
            raise ValueError(f"cell {key!r} metadata must be a mapping")
        if cell.get("participates") is True:
            missing = required.difference(cell)
            if missing:
                raise ValueError(
                    f"participating cell {key!r} missing metadata {sorted(missing)!r}"
                )
            if cell.get("legality") not in LEGALITIES:
                raise ValueError(f"participating cell {key!r} has invalid legality")


def select_subevents(unit: Mapping[str, Any]) -> dict[str, object]:
    candidates = tuple(unit.get("candidates") or ())
    secondary = tuple(unit.get("secondary") or ())
    explicit_primary = unit.get("primary")
    handler_target = unit.get("handler_target")

    if explicit_primary is not None:
        primary = explicit_primary
    elif handler_target is not None:
        primary = handler_target
    elif len(candidates) == 1:
        primary = candidates[0]
    else:
        raise ValueError("primary subevent is ambiguous or missing")

    if not isinstance(primary, str) or not primary:
        raise ValueError("primary subevent is missing")
    if candidates and primary not in candidates:
        raise ValueError("primary subevent is not present in candidates")
    if primary in secondary:
        raise ValueError("primary subevent cannot also be secondary")

    if not secondary and candidates:
        secondary = tuple(candidate for candidate in candidates if candidate != primary)
    if primary in secondary:
        raise ValueError("primary subevent cannot also be secondary")

    return {
        "family": unit.get("family"),
        "primary": primary,
        "secondary": secondary,
    }


__all__ = [
    "build_lifecycle_matrix",
    "select_subevents",
    "validate_lifecycle_matrix",
]
