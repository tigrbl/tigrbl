from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, Mapping


def _rows(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, Mapping):
        items = payload.get("rows", ())
    else:
        items = payload
    if not isinstance(items, Iterable) or isinstance(items, (str, bytes)):
        raise TypeError("OLAP operations require iterable row payloads")
    materialized = list(items)
    non_mappings = [item for item in materialized if not isinstance(item, Mapping)]
    if non_mappings:
        raise TypeError("OLAP row payloads must contain mappings")
    rows = [row for row in materialized if isinstance(row, Mapping)]
    return rows


def _coerce_numeric(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"Expected numeric value, got {type(value).__name__}")


async def aggregate(payload: Any) -> Dict[str, Any]:
    body = payload if isinstance(payload, Mapping) else {"rows": payload}
    rows = _rows(body)
    field = body.get("field")
    op = str(body.get("op", "sum")).lower()
    if not isinstance(field, str) or not field:
        raise TypeError("aggregate requires a non-empty 'field'")
    values = [_coerce_numeric(row[field]) for row in rows if field in row]
    if op == "sum":
        result = sum(values)
    elif op == "avg":
        result = (sum(values) / len(values)) if values else 0.0
    elif op == "min":
        result = min(values) if values else None
    elif op == "max":
        result = max(values) if values else None
    elif op == "count":
        result = len(values)
    else:
        raise ValueError(f"Unsupported aggregate op: {op}")
    return {"field": field, "op": op, "value": result, "count": len(values)}


async def group_by(payload: Any) -> Dict[str, Any]:
    body = payload if isinstance(payload, Mapping) else {"rows": payload}
    rows = _rows(body)
    field = body.get("field")
    value_field = body.get("value_field")
    agg = str(body.get("agg", "count")).lower()
    if not isinstance(field, str) or not field:
        raise TypeError("group_by requires a non-empty 'field'")

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field))].append(row)

    items: list[Dict[str, Any]] = []
    for key, group in grouped.items():
        if agg == "count":
            value: Any = len(group)
        else:
            if not isinstance(value_field, str) or not value_field:
                raise TypeError("group_by requires 'value_field' for numeric aggregates")
            numerics = [
                _coerce_numeric(row[value_field]) for row in group if value_field in row
            ]
            if agg == "sum":
                value = sum(numerics)
            elif agg == "avg":
                value = (sum(numerics) / len(numerics)) if numerics else 0.0
            elif agg == "min":
                value = min(numerics) if numerics else None
            elif agg == "max":
                value = max(numerics) if numerics else None
            else:
                raise ValueError(f"Unsupported group_by aggregate: {agg}")
        items.append({"key": key, "value": value, "rows": len(group)})
    items.sort(key=lambda item: item["key"])
    return {"field": field, "agg": agg, "groups": items}
