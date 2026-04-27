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
    assert {"HANDLER", "POST_RESPONSE", "POST_EMIT"} <= set(matrix["phases"])


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


def test_matrix_cells_distinguish_required_optional_and_forbidden_legality() -> None:
    build_matrix = _require("tigrbl_kernel.lifecycle_matrix", "build_lifecycle_matrix")

    matrix = build_matrix()
    legalities = {
        cell["legality"]
        for cell in matrix["cells"].values()
        if cell.get("participates") is True
    }

    assert {"required", "optional", "forbidden"} <= legalities


def test_matrix_validation_requires_cell_metadata_for_participating_cells() -> None:
    validate_matrix = _require("tigrbl_kernel.lifecycle_matrix", "validate_lifecycle_matrix")

    with pytest.raises(ValueError, match="cell|metadata|legality|hookable|tx_unit"):
        validate_matrix(
            {
                "phases": ("HANDLER",),
                "rows": [{"family": "socket", "subevent": "message.received"}],
                "cells": {
                    ("socket", "message.received", "HANDLER"): {
                        "participates": True,
                    }
                },
            }
        )


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


def test_phases_are_not_accepted_as_subevent_rows() -> None:
    validate_matrix = _require("tigrbl_kernel.lifecycle_matrix", "validate_lifecycle_matrix")

    with pytest.raises(ValueError, match="family|subevent|phase|axis"):
        validate_matrix(
            {
                "phases": ("HANDLER", "POST_RESPONSE"),
                "rows": [{"family": "socket", "subevent": "HANDLER"}],
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


def test_primary_subevent_selection_preserves_secondary_annotation_order() -> None:
    select_subevents = _require("tigrbl_kernel.lifecycle_matrix", "select_subevents")

    result = select_subevents(
        {
            "family": "event_stream",
            "candidates": ("message.encoded", "message.emit", "message.queued"),
            "handler_target": "message.emit",
        }
    )

    assert result["primary"] == "message.emit"
    assert result["secondary"] == ("message.encoded", "message.queued")


@pytest.mark.parametrize(
    "unit",
    (
        {"family": "socket", "candidates": ()},
        {"family": "socket", "candidates": ("message.received", "message.closed")},
        {"family": "socket", "handler_target": "message.decoded", "secondary": ("message.decoded",)},
        {"family": "socket", "candidates": ("message.received",), "primary": "message.received", "secondary": ("message.received",)},
    ),
)
def test_primary_subevent_selection_fails_closed_for_ambiguous_or_missing_primary(
    unit: dict[str, object],
) -> None:
    select_subevents = _require("tigrbl_kernel.lifecycle_matrix", "select_subevents")

    with pytest.raises(ValueError, match="primary|subevent|ambiguous|secondary"):
        select_subevents(unit)
