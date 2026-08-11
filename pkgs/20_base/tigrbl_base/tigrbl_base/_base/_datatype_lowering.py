from __future__ import annotations

import datetime as dt
from decimal import Decimal
from types import UnionType
from typing import Any
from typing import Union, get_args, get_origin
from uuid import UUID

from tigrbl_core._spec.datatypes import DataTypeSpec


def lower_datatype_to_sqla_type(
    datatype: DataTypeSpec | None, *, field: Any = None
) -> Any:
    """Lower a canonical datatype into a SQLAlchemy type/instance."""

    if datatype is None:
        py_type = getattr(field, "py_type", None)
        origin = get_origin(py_type)
        if origin in (Union, UnionType):
            members = tuple(
                member for member in get_args(py_type) if member is not type(None)
            )
            py_type = members[0] if len(members) == 1 else py_type

        logical_by_python_type = {
            str: "string",
            int: "integer",
            float: "number",
            Decimal: "decimal",
            bool: "boolean",
            bytes: "bytes",
            dt.date: "date",
            dt.datetime: "datetime",
            dt.time: "time",
            dict: "object",
            list: "array",
            UUID: "uuid",
        }
        logical_name = logical_by_python_type.get(py_type)
        if logical_name is None:
            return None
        datatype = DataTypeSpec(logical_name=logical_name)

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
