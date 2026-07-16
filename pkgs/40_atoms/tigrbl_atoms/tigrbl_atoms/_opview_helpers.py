from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_READ_ONLY_TARGETS = frozenset(
    {"read", "list", "count", "exists", "aggregate", "group_by", "subscribe", "tail", "download"}
)
_NON_PERSISTING_TARGETS = frozenset(
    {"delete", "clear", "bulk_delete", "close_stream", "close_session"}
)
_CREATE_LIKE_TARGETS = frozenset({"create", "bulk_create"})
_UPDATE_LIKE_TARGETS = frozenset({"update", "merge", "bulk_update", "bulk_merge"})
_REPLACE_LIKE_TARGETS = frozenset({"replace", "bulk_replace"})


def _storage_requires_input(storage: Any, op: str) -> bool:
    if storage is None or op == "update":
        return False
    if bool(getattr(storage, "primary_key", False)):
        if op in {"replace", "delete"}:
            return True
        auto = getattr(storage, "autoincrement", False)
        if auto not in (False, None) or getattr(storage, "identity", None) is not None:
            return False
    has_default = (
        getattr(storage, "default", None) is not None
        or getattr(storage, "server_default", None) is not None
        or callable(getattr(storage, "default_factory", None))
    )
    return not bool(getattr(storage, "nullable", True)) and not has_default


def _storage_has_server_default(spec: Any, storage: Any) -> bool:
    return bool(
        getattr(storage, "default", None) is not None
        or getattr(storage, "server_default", None) is not None
        or callable(getattr(storage, "default_factory", None))
        or callable(getattr(spec, "default_factory", None))
    )


def _supports_stored_shape(op: str) -> bool:
    lowered = str(op or "").lower()
    return lowered not in _READ_ONLY_TARGETS and lowered not in _NON_PERSISTING_TARGETS


def _is_input_enabled(io: Any, op: str) -> bool:
    return op in set(getattr(io, "in_verbs", ()) or ())


def _is_paired_enabled(io: Any, op: str) -> bool:
    cfg = getattr(io, "_paired", None)
    if cfg is None:
        return False
    return op in set(getattr(cfg, "verbs", ()) or ())


def _include_in_stored_schema(spec: Any, io: Any, storage: Any, op: str) -> bool:
    lowered = str(op or "").lower()
    if storage is None or not _supports_stored_shape(lowered):
        return False
    if _is_input_enabled(io, op) or _is_paired_enabled(io, op):
        return True
    if lowered in _CREATE_LIKE_TARGETS or lowered in _UPDATE_LIKE_TARGETS:
        return True
    if lowered in _REPLACE_LIKE_TARGETS:
        return True
    return False


def _stored_required(spec: Any, storage: Any, op: str, *, derived: bool) -> bool:
    lowered = str(op or "").lower()
    if lowered in _UPDATE_LIKE_TARGETS:
        return False
    if lowered in _READ_ONLY_TARGETS or lowered in _NON_PERSISTING_TARGETS:
        return False
    if derived:
        return True
    return not bool(getattr(storage, "nullable", True)) and not _storage_has_server_default(
        spec,
        storage,
    )


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _ensure_ov(ctx: Any):
    ov = getattr(ctx, "opview", None)
    if ov is None:
        raise RuntimeError("ctx_missing:opview")
    return ov


def _normalize_schema_from_specs(ctx: Any) -> None:
    specs = getattr(ctx, "specs", None)
    op = getattr(ctx, "op", None)
    if not isinstance(specs, Mapping) or not isinstance(op, str) or not op:
        raise RuntimeError("ctx_missing:opview")

    in_fields: list[str] = []
    out_fields: list[str] = []
    stored_fields: list[str] = []
    by_field_in: dict[str, dict[str, Any]] = {}
    by_field_out: dict[str, dict[str, Any]] = {}
    by_field_stored: dict[str, dict[str, Any]] = {}
    required_from_client: list[str] = []

    for field_name, spec in specs.items():
        if not isinstance(field_name, str):
            continue
        io = getattr(spec, "io", None)
        fs = getattr(spec, "field", None)
        storage = getattr(spec, "storage", None)

        in_verbs = set(getattr(io, "in_verbs", ()) or ())
        out_verbs = set(getattr(io, "out_verbs", ()) or ())

        if op in in_verbs:
            in_fields.append(field_name)
            in_meta: dict[str, Any] = {"in_enabled": True}
            if storage is None:
                in_meta["virtual"] = True
            py_type = getattr(fs, "py_type", None)
            if py_type is not None and py_type is not Any:
                in_meta["py_type"] = py_type
            constraints = getattr(fs, "constraints", {}) or {}
            if isinstance(constraints, Mapping):
                max_length = constraints.get("max_length")
                if isinstance(max_length, int) and max_length > 0:
                    in_meta["max_length"] = max_length

            default_factory = getattr(spec, "default_factory", None)
            if callable(default_factory):
                in_meta["default_factory"] = default_factory

            alias_in = getattr(io, "alias_in", None)
            if alias_in:
                in_meta["alias_in"] = alias_in

            header_in = getattr(io, "header_in", None)
            if header_in:
                in_meta["header_in"] = header_in
                in_meta["header_required_in"] = bool(
                    getattr(io, "header_required_in", False)
                )

            in_meta["required"] = bool(
                (fs and op in getattr(fs, "required_in", ()))
                or _storage_requires_input(storage, op)
            )
            in_meta["nullable"] = (
                True if storage is None else bool(getattr(storage, "nullable", True))
            )
            in_meta["coerce"] = True
            by_field_in[field_name] = in_meta

        if op in out_verbs:
            out_fields.append(field_name)
            out_meta: dict[str, Any] = {}

            alias_out = getattr(io, "alias_out", None)
            if alias_out:
                out_meta["alias_out"] = alias_out
            if storage is None:
                out_meta["virtual"] = True

            py_type = getattr(getattr(fs, "py_type", None), "__name__", None)
            if py_type:
                out_meta["py_type"] = py_type
            by_field_out[field_name] = out_meta

        if _include_in_stored_schema(spec, io, storage, op):
            stored_fields.append(field_name)
            input_enabled = _is_input_enabled(io, op)
            paired_enabled = _is_paired_enabled(io, op)
            server_default = _storage_has_server_default(spec, storage)
            py_type = getattr(fs, "py_type", None) if fs is not None else None
            if py_type is not None and py_type is not Any:
                resolved_py_type = py_type
            else:
                storage_type = getattr(storage, "type_", None)
                resolved_py_type = (
                    Any
                    if storage_type is None
                    else getattr(storage_type, "python_type", Any)
                )
            stored_meta: dict[str, Any] = {
                "nullable": bool(getattr(storage, "nullable", True)),
                "from_client": input_enabled,
                "required_from_client": bool(
                    input_enabled and _storage_requires_input(storage, op)
                ),
                "server_default": server_default,
            }
            if resolved_py_type is not Any:
                stored_meta["py_type"] = resolved_py_type
            constraints = getattr(fs, "constraints", {}) or {}
            if isinstance(constraints, Mapping):
                max_length = constraints.get("max_length")
                if isinstance(max_length, int) and max_length > 0:
                    stored_meta["max_length"] = max_length
            derived = paired_enabled or callable(
                getattr(getattr(storage, "transform", None), "to_stored", None)
            )
            stored_meta["derived"] = derived
            stored_meta["required"] = _stored_required(
                spec,
                storage,
                op,
                derived=derived,
            )
            if stored_meta["required_from_client"]:
                required_from_client.append(field_name)
            by_field_stored[field_name] = stored_meta

    in_fields_sorted = tuple(sorted(in_fields))
    out_fields_sorted = tuple(sorted(out_fields))
    stored_fields_sorted = tuple(sorted(stored_fields))

    setattr(
        ctx,
        "schema_in",
        {
            "fields": in_fields_sorted,
            "by_field": {f: by_field_in.get(f, {}) for f in in_fields_sorted},
            "required": tuple(
                f for f in in_fields_sorted if by_field_in.get(f, {}).get("required")
            ),
        },
    )
    setattr(
        ctx,
        "schema_out",
        {
            "fields": out_fields_sorted,
            "by_field": {f: by_field_out.get(f, {}) for f in out_fields_sorted},
            "expose": out_fields_sorted,
        },
    )
    setattr(
        ctx,
        "schema_stored",
        {
            "fields": stored_fields_sorted,
            "by_field": {f: by_field_stored.get(f, {}) for f in stored_fields_sorted},
            "required_from_client": tuple(sorted(required_from_client)),
            "required": tuple(
                f
                for f in stored_fields_sorted
                if by_field_stored.get(f, {}).get("required")
            ),
        },
    )


def _ensure_schema_in(ctx: Any) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    cached = temp.get("schema_in")
    if isinstance(cached, Mapping):
        return cached

    schema_in = getattr(ctx, "schema_in", None)
    if isinstance(schema_in, Mapping):
        temp["schema_in"] = schema_in
        return schema_in

    try:
        ov = _ensure_ov(ctx)
        bf = ov.schema_in.by_field
        req = tuple(n for n, e in bf.items() if e.get("required"))
        temp["schema_in"] = {
            "fields": ov.schema_in.fields,
            "by_field": bf,
            "required": req,
        }
    except RuntimeError as exc:
        if str(exc) != "ctx_missing:opview":
            raise
        _normalize_schema_from_specs(ctx)
        temp["schema_in"] = getattr(ctx, "schema_in")
    return temp["schema_in"]


def _ensure_schema_out(ctx: Any) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    cached = temp.get("schema_out")
    if isinstance(cached, Mapping):
        return cached

    schema_out = getattr(ctx, "schema_out", None)
    if isinstance(schema_out, Mapping):
        temp["schema_out"] = schema_out
        return schema_out

    try:
        ov = _ensure_ov(ctx)
        temp["schema_out"] = {
            "fields": ov.schema_out.fields,
            "by_field": ov.schema_out.by_field,
            "expose": ov.schema_out.expose,
        }
    except RuntimeError as exc:
        if str(exc) != "ctx_missing:opview":
            raise
        _normalize_schema_from_specs(ctx)
        temp["schema_out"] = getattr(ctx, "schema_out")
    return temp["schema_out"]


def _ensure_schema_stored(ctx: Any) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    cached = temp.get("schema_stored")
    if isinstance(cached, Mapping):
        return cached

    schema_stored = getattr(ctx, "schema_stored", None)
    if isinstance(schema_stored, Mapping):
        temp["schema_stored"] = schema_stored
        return schema_stored

    try:
        ov = _ensure_ov(ctx)
        stored = getattr(ov, "schema_stored", None)
        if stored is None:
            raise RuntimeError("ctx_missing:opview")
        temp["schema_stored"] = {
            "fields": stored.fields,
            "by_field": stored.by_field,
            "required_from_client": getattr(stored, "required_from_client", ()),
            "required": tuple(
                field
                for field, meta in getattr(stored, "by_field", {}).items()
                if meta.get("required")
            ),
        }
    except RuntimeError as exc:
        if str(exc) != "ctx_missing:opview":
            raise
        _normalize_schema_from_specs(ctx)
        temp["schema_stored"] = getattr(ctx, "schema_stored")
    return temp["schema_stored"]
