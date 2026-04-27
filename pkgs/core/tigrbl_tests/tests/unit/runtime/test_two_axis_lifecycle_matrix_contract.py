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


def test_two_axis_matrix_uses_family_subevent_rows_and_phase_columns() -> None:
    build_matrix = _require("tigrbl_kernel.lifecycle_matrix", "build_lifecycle_matrix")

    matrix = build_matrix()

    assert "phases" in matrix
    assert "rows" in matrix
    assert "INGRESS_ROUTE" not in matrix["phases"]
    assert {"family", "subevent"} <= set(matrix["rows"][0])
    assert {"socket", "event_stream", "stream"} <= {row["family"] for row in matrix["rows"]}
    assert "message.received" in {row["subevent"] for row in matrix["rows"]}


def test_matrix_cells_declare_compiler_metadata() -> None:
    build_matrix = _require("tigrbl_kernel.lifecycle_matrix", "build_lifecycle_matrix")

    matrix = build_matrix()
    cell = matrix["cells"][("socket", "message.received", "HANDLER")]

    assert {
        "participates",
        "hookable",
        "tx_unit",
        "loop_region",
        "legality",
    } <= set(cell)
    assert cell["participates"] is True
    assert cell["legality"] in {"required", "optional", "forbidden", "repeated"}


def test_subevents_are_not_accepted_as_phase_columns() -> None:
    validate_matrix = _require("tigrbl_kernel.lifecycle_matrix", "validate_lifecycle_matrix")

    with pytest.raises(ValueError, match="subevent|phase|axis"):
        validate_matrix(
            {
                "phases": ("message.received", "HANDLER"),
                "rows": [{"family": "socket", "subevent": "message.received"}],
                "cells": {},
            }
        )


def test_executable_unit_selects_one_primary_subevent_and_secondary_annotations() -> None:
    select_subevents = _require("tigrbl_kernel.lifecycle_matrix", "select_subevents")

    result = select_subevents(
        {
            "family": "socket",
            "candidates": ("message.decoded", "message.received"),
            "handler_target": "message.received",
        }
    )

    assert result["primary"] == "message.received"
    assert result["secondary"] == ("message.decoded",)


@pytest.mark.parametrize(
    "unit",
    (
        {"family": "socket", "candidates": ()},
        {"family": "socket", "candidates": ("message.received", "message.closed")},
        {"family": "socket", "handler_target": "message.decoded", "secondary": ("message.decoded",)},
    ),
)
def test_primary_subevent_selection_fails_closed_for_ambiguous_or_missing_primary(
    unit: dict[str, object],
) -> None:
    select_subevents = _require("tigrbl_kernel.lifecycle_matrix", "select_subevents")

    with pytest.raises(ValueError, match="primary|subevent|ambiguous|secondary"):
        select_subevents(unit)

