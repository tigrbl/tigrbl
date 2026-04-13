from __future__ import annotations

from typing import Any

from tigrbl_core._spec.datatypes import DataTypeSpec


def lower_datatype_to_sqla_type(datatype: DataTypeSpec | None, *, field: Any = None) -> Any:
    """Lower a canonical datatype into a SQLAlchemy type/instance."""

    if datatype is None:
        return None

    from sqlalchemy import (
        JSON,
        Boolean,
        Date,
        DateTime,
        Float,
        Integer,
        LargeBinary,
        Numeric,
        String,
        Time,
    )

    logical = datatype.logical_name
    options = dict(getattr(datatype, "options", {}) or {})
    max_length = options.get("max_length")
    if max_length is None and field is not None:
        constraints = getattr(field, "constraints", {}) or {}
        max_length = constraints.get("max_length")

    if logical in {"string", "uuid", "ulid"}:
        return String(max_length) if max_length else String()
    if logical == "integer":
        return Integer()
    if logical == "number":
        return Float()
    if logical == "decimal":
        return Numeric()
    if logical == "boolean":
        return Boolean()
    if logical == "bytes":
        return LargeBinary()
    if logical == "date":
        return Date()
    if logical == "datetime":
        return DateTime()
    if logical == "time":
        return Time()
    if logical in {"json", "array", "object"}:
        return JSON()
    if logical == "duration":
        try:
            from sqlalchemy import Interval

            return Interval()
        except Exception:
            return String()
    return String(max_length) if max_length else String()
