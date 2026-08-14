"""Generic access to canonical operations bound on concrete tables."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping
from typing import Any


async def maybe_await(value: object | Awaitable[object]) -> object:
    return await value if inspect.isawaitable(value) else value


def payload_from_context(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ctx.get("payload", ctx.get("data", {}))
    if not isinstance(payload, Mapping):
        raise TypeError("table operation payload must be a mapping")
    return payload


def database_from_context(ctx: Mapping[str, Any]) -> Any:
    try:
        return ctx["db"]
    except KeyError as exc:
        raise ValueError("table operation requires a database session") from exc


def field_value(row: Any, key: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(key, default)
    return getattr(row, key, default)


def record_identifier(row: Any) -> Any:
    return field_value(row, "id")


def _single_primary_key_name(table: type) -> str:
    bound_table = getattr(table, "__table__", None)
    primary_key = getattr(bound_table, "primary_key", None)
    columns = tuple(getattr(primary_key, "columns", ()) or ())
    if len(columns) != 1:
        raise ValueError(f"{table.__name__} must have exactly one primary key")
    return str(columns[0].name)


def _operation_target(table: type, alias: str) -> str:
    by_alias = getattr(getattr(table, "ops", None), "by_alias", {})
    operation = by_alias.get(alias) if isinstance(by_alias, Mapping) else None
    return str(getattr(operation, "target", alias))


def normalize_items(result: Any) -> list[Any]:
    if isinstance(result, Mapping):
        result = result.get("items", result.get("data", result))
    elif hasattr(result, "items") and not isinstance(result, (list, tuple)):
        result = result.items
    if result is None:
        return []
    return list(result) if isinstance(result, (list, tuple)) else [result]


async def invoke_table_operation(
    table: type,
    alias: str,
    *,
    db: Any,
    payload: Any = None,
    path_params: Mapping[str, Any] | None = None,
) -> Any:
    """Invoke a canonical table-bound core with a normalized context."""

    namespace = getattr(getattr(table, "handlers", None), alias, None)
    core = getattr(namespace, "core", None)
    if not callable(core):
        raise LookupError(f"{table.__name__}.{alias} is not bound")
    return await maybe_await(
        core(
            {
                "model": table,
                "op": alias,
                "target": _operation_target(table, alias),
                "db": db,
                "payload": {} if payload is None else payload,
                "path_params": dict(path_params or {}),
            }
        )
    )


async def create_table_record(table: type, db: Any, payload: Mapping[str, Any]) -> Any:
    result = await invoke_table_operation(table, "create", db=db, payload=dict(payload))
    return result.get("item", result) if isinstance(result, Mapping) else result


async def read_table_record(table: type, db: Any, ident: Any) -> Any:
    return await invoke_table_operation(
        table,
        "read",
        db=db,
        path_params={_single_primary_key_name(table): ident},
    )


async def update_table_record(
    table: type, db: Any, ident: Any, payload: Mapping[str, Any]
) -> Any:
    result = await invoke_table_operation(
        table,
        "update",
        db=db,
        payload=dict(payload),
        path_params={_single_primary_key_name(table): ident},
    )
    return result.get("item", result) if isinstance(result, Mapping) else result


async def delete_table_record(table: type, db: Any, ident: Any) -> Any:
    return await invoke_table_operation(
        table,
        "delete",
        db=db,
        path_params={_single_primary_key_name(table): ident},
    )


async def list_table_records(
    table: type, db: Any, filters: Mapping[str, Any] | None = None
) -> list[Any]:
    selected = dict(filters or {})
    result = await invoke_table_operation(table, "list", db=db, payload=selected)
    return normalize_items(result)


async def first_table_record(table: type, db: Any, filters: Mapping[str, Any]) -> Any:
    rows = await list_table_records(table, db, filters)
    return rows[0] if rows else None


async def clear_table_records(
    table: type, db: Any, filters: Mapping[str, Any] | None = None
) -> Any:
    return await invoke_table_operation(
        table, "clear", db=db, payload={"filters": dict(filters or {})}
    )


def provideTableHandler(
    table: type,
    alias: str = "create",
    *,
    payload_validator: Callable[[Mapping[str, Any]], None] | None = None,
) -> Callable[[Mapping[str, Any]], Awaitable[Any]]:
    """Provide a deferred context handler for a canonical table operation."""

    async def provided(ctx: Mapping[str, Any]) -> Any:
        payload = payload_from_context(ctx)
        if payload_validator is not None:
            payload_validator(payload)
        return await invoke_table_operation(
            table,
            alias,
            db=database_from_context(ctx),
            payload=payload,
            path_params=ctx.get("path_params"),
        )

    provided.__name__ = f"{alias}_{table.__name__}"
    return provided


field = field_value
record_id = record_identifier
create_record = create_table_record
read_record = read_table_record
update_record = update_table_record
delete_record = delete_table_record
list_records = list_table_records
first_record = first_table_record
clear_records = clear_table_records


__all__ = [
    "clear_table_records",
    "clear_records",
    "create_table_record",
    "create_record",
    "database_from_context",
    "delete_table_record",
    "delete_record",
    "field",
    "field_value",
    "first_table_record",
    "first_record",
    "invoke_table_operation",
    "list_table_records",
    "list_records",
    "maybe_await",
    "normalize_items",
    "payload_from_context",
    "provideTableHandler",
    "read_table_record",
    "read_record",
    "record_identifier",
    "update_table_record",
    "update_record",
]
