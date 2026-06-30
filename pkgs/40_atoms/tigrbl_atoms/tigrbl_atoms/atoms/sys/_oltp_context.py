from __future__ import annotations

import json
import uuid
from typing import Any, Mapping, Optional, Sequence

try:  # pragma: no cover
    from sqlalchemy.inspection import inspect as _sa_inspect  # type: ignore
except Exception:  # pragma: no cover
    _sa_inspect = None  # type: ignore

try:  # pragma: no cover
    from sqlalchemy.sql import ClauseElement as SAClause  # type: ignore
except Exception:  # pragma: no cover
    SAClause = None  # type: ignore


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)


def payload(ctx: Mapping[str, Any]) -> Any:
    temp = _ctx_get(ctx, "temp", None)
    raw = _ctx_get(ctx, "payload", None)
    if isinstance(temp, Mapping):
        assembled_values = temp.get("assembled_values")
        if isinstance(assembled_values, Mapping):
            if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
                if not assembled_values:
                    return raw
                merged_items: list[Any] = []
                changed = False
                for item in raw:
                    if not isinstance(item, Mapping):
                        merged_items.append(item)
                        continue
                    merged = dict(assembled_values)
                    merged.update(item)
                    changed = changed or merged != item
                    merged_items.append(merged)
                if changed:
                    return merged_items
                return raw
            if not assembled_values and isinstance(raw, Mapping):
                return raw
            if isinstance(raw, Mapping):
                try:
                    if all(key in assembled_values for key in raw):
                        return assembled_values
                except Exception:
                    pass
                merged = dict(raw)
                merged.update(assembled_values)
                return merged
            return assembled_values

        route = temp.get("route")
        if isinstance(route, Mapping):
            route_payload = route.get("payload")
            if isinstance(route_payload, Mapping):
                return route_payload
            if isinstance(route_payload, Sequence) and not isinstance(
                route_payload, (str, bytes)
            ):
                return route_payload
            rpc_envelope = route.get("rpc_envelope")
            if isinstance(rpc_envelope, Mapping):
                params = rpc_envelope.get("params")
                if isinstance(params, Mapping):
                    return params
                if isinstance(params, Sequence) and not isinstance(
                    params, (str, bytes)
                ):
                    return params

        dispatch = temp.get("dispatch")
        if isinstance(dispatch, Mapping):
            parsed_payload = dispatch.get("parsed_payload")
            if isinstance(parsed_payload, Mapping):
                return parsed_payload
            if isinstance(parsed_payload, Sequence) and not isinstance(
                parsed_payload, (str, bytes)
            ):
                return parsed_payload
            rpc_envelope = dispatch.get("rpc")
            if isinstance(rpc_envelope, Mapping):
                params = rpc_envelope.get("params")
                if isinstance(params, Mapping):
                    return params
                if isinstance(params, Sequence) and not isinstance(
                    params, (str, bytes)
                ):
                    return params

    body = _ctx_get(ctx, "body", None)
    request_obj = _ctx_get(ctx, "request", None)
    if body is None and request_obj is not None:
        body = getattr(request_obj, "body", None)
    if isinstance(body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            body = None
    if isinstance(body, Mapping) and body.get("jsonrpc") == "2.0":
        params = body.get("params")
        if isinstance(params, Mapping):
            return params
        if isinstance(params, Sequence) and not isinstance(params, (str, bytes)):
            return params
    if isinstance(body, Mapping):
        return body
    if isinstance(body, Sequence) and not isinstance(body, (str, bytes)):
        return body

    if isinstance(raw, Mapping):
        return raw
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        return raw
    return {}


def db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db") or _ctx_get(ctx, "_raw_db")


def request(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "request")


def path_params(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    params = _ctx_get(ctx, "path_params", None)
    if isinstance(params, Mapping):
        return params

    temp = _ctx_get(ctx, "temp", None)
    if isinstance(temp, Mapping):
        route = temp.get("route")
        if isinstance(route, Mapping):
            route_params = route.get("path_params")
            if isinstance(route_params, Mapping):
                return route_params
    return {}


def _pk_name(model: type) -> str:
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            if len(pk_cols) == 1:
                col = pk_cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass

    table = getattr(model, "__table__", None)
    if table is not None:
        try:
            pk = getattr(table, "primary_key", None)
            cols_iter = getattr(pk, "columns", None)
            cols = [col for col in cols_iter] if cols_iter is not None else []
            if len(cols) == 1:
                col = cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass
    return "id"


def _pk_type_info(model: type) -> tuple[Optional[type], Optional[Any]]:
    col = None
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            if len(pk_cols) == 1:
                col = pk_cols[0]
        except Exception:
            col = None

    if col is None:
        table = getattr(model, "__table__", None)
        if table is not None:
            try:
                pk = getattr(table, "primary_key", None)
                cols_iter = getattr(pk, "columns", None)
                cols = [item for item in cols_iter] if cols_iter is not None else []
                if len(cols) == 1:
                    col = cols[0]
            except Exception:
                col = None

    if col is None:
        return (None, None)

    try:
        col_type = getattr(col, "type", None)
    except Exception:
        col_type = None

    py_t = None
    try:
        py_t = getattr(col_type, "python_type", None)
    except Exception:
        py_t = None

    return (py_t, col_type)


def _is_uuid_type(py_t: Optional[type], sa_type: Optional[Any]) -> bool:
    if py_t is uuid.UUID:
        return True
    try:
        if getattr(sa_type, "as_uuid", False):
            return True
    except Exception:
        pass
    try:
        type_name = type(sa_type).__name__.lower() if sa_type is not None else ""
        if "uuid" in type_name:
            return True
    except Exception:
        pass
    return False


def _coerce_ident_to_pk_type(model: type, value: Any) -> Any:
    py_t, sa_t = _pk_type_info(model)

    if SAClause is not None and isinstance(value, SAClause):  # pragma: no cover
        return value

    if _is_uuid_type(py_t, sa_t):
        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, str):
            return uuid.UUID(value)
        if isinstance(value, (bytes, bytearray)) and len(value) == 16:
            return uuid.UUID(bytes=bytes(value))
        return value

    if py_t is int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception:
            return value

    return value


def _is_clause(value: Any) -> bool:
    return SAClause is not None and isinstance(value, SAClause)  # type: ignore[truthy-bool]


def ident(model: type, ctx: Mapping[str, Any]) -> Any:
    model_payload = payload(ctx)
    model_path = path_params(ctx)
    pk = _pk_name(model)

    candidates: list[tuple[Mapping[str, Any], str]] = [
        (model_path, pk),
        (model_payload, pk),
        (model_path, "id"),
        (model_payload, "id"),
        (model_path, "item_id"),
        (model_payload, "item_id"),
    ]
    if pk != "id":
        candidates.extend([(model_path, f"{pk}_id"), (model_payload, f"{pk}_id")])
    candidates.append((model_payload, "ident"))

    for source, key in candidates:
        try:
            value = source.get(key)
        except Exception:
            value = None
        if value is None or _is_clause(value):
            continue
        try:
            return _coerce_ident_to_pk_type(model, value)
        except Exception as exc:
            raise TypeError(f"Invalid identifier for '{pk}': {value!r}") from exc

    temp = _ctx_get(ctx, "temp", None)
    if isinstance(temp, Mapping):
        rpc_sources = []
        route = temp.get("route")
        if isinstance(route, Mapping):
            rpc_sources.append(route.get("rpc_envelope"))
        dispatch = temp.get("dispatch")
        if isinstance(dispatch, Mapping):
            rpc_sources.append(dispatch.get("rpc"))
        for envelope in rpc_sources:
            if not isinstance(envelope, Mapping):
                continue
            params = envelope.get("params")
            if not isinstance(params, Mapping):
                continue
            for key in (pk, "id", "item_id", f"{pk}_id", "ident"):
                value = params.get(key)
                if value is None or _is_clause(value):
                    continue
                try:
                    return _coerce_ident_to_pk_type(model, value)
                except Exception as exc:
                    raise TypeError(
                        f"Invalid identifier for '{pk}': {value!r}"
                    ) from exc

    raise TypeError(f"Missing identifier '{pk}' in path or payload")


__all__ = ["db", "ident", "path_params", "payload", "request"]
