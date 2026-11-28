"""Schema builders for list parameter models."""

from __future__ import annotations

import logging
from typing import Any, Type

from pydantic import BaseModel, ConfigDict, Field, create_model

from ..utils import namely_model
from tigrbl_core._spec.column_spec import ColumnSpec

logger = logging.getLogger(__name__)


def _build_list_params(model: type) -> Type[BaseModel]:
    """Create a list/filter schema for the given model."""
    tab = model.__name__
    logger.debug("schema: build_list_params for %s", tab)

    base = dict(
        skip=(int | None, Field(None, ge=0)),
        limit=(int | None, Field(None, ge=10)),
        sort=(str | list[str] | None, Field(None)),
    )
    cols: dict[str, tuple[Any, Any]] = {}

    table = getattr(model, "__table__", None)
    if table is None or not getattr(table, "columns", None):
        # No table info; return a minimal pager schema
        schema = create_model(
            f"{tab}ListParams", __config__=ConfigDict(extra="forbid"), **base
        )  # type: ignore[arg-type]
        schema = namely_model(
            schema,
            name=f"{tab}ListParams",
            doc=f"List parameters for {tab}",
        )
        logger.debug(
            "schema: build_list_params generated %s (no columns)", schema.__name__
        )
        return schema

    _canon = {
        "eq": "eq",
        "=": "eq",
        "==": "eq",
        "ne": "ne",
        "!=": "ne",
        "<>": "ne",
        "lt": "lt",
        "<": "lt",
        "gt": "gt",
        ">": "gt",
        "lte": "lte",
        "le": "lte",
        "<=": "lte",
        "gte": "gte",
        "ge": "gte",
        ">=": "gte",
        "like": "like",
        "not_like": "not_like",
        "ilike": "ilike",
        "not_ilike": "not_ilike",
        "in": "in",
        "not_in": "not_in",
    }

    spec_map = ColumnSpec.collect(model)
    for c in table.columns:
        try:
            py_t = c.type.python_type
        except Exception:
            py_t = Any
        spec = spec_map.get(c.name)
        io = getattr(spec, "io", None)
        ops_raw = set(getattr(io, "filter_ops", ()) or [])
        if not ops_raw:
            ops_raw = {"eq"}
        ops = {_canon.get(op, op) for op in ops_raw}
        if "eq" in ops:
            cols[c.name] = (py_t | None, Field(None))
            logger.debug("schema: list filter add %s type=%r", c.name, py_t)
        for op in ops:
            if op == "eq":
                continue
            fname = f"{c.name}__{op}"
            annotation = list[py_t] | None if op in {"in", "not_in"} else py_t | None
            cols[fname] = (annotation, Field(None))
            logger.debug("schema: list filter add %s op=%s type=%r", c.name, op, py_t)

    schema = create_model(
        f"{tab}ListParams",
        __config__=ConfigDict(extra="forbid"),
        **base,  # type: ignore[arg-type]
        **cols,  # type: ignore[arg-type]
    )
    schema = namely_model(
        schema,
        name=f"{tab}ListParams",
        doc=f"List parameters for {tab}",
    )
    logger.debug("schema: build_list_params generated %s", schema.__name__)
    return schema


__all__ = ["_build_list_params"]
