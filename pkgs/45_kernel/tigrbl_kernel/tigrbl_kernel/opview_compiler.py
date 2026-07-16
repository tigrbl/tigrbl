from __future__ import annotations

from typing import Any, Dict, Mapping

from tigrbl_core.schema.builder.helpers import _normalize_py_type, _storage_python_type

from .models import OpView, SchemaIn, SchemaOut, SchemaStored

_READ_ONLY_TARGETS = frozenset(
    {
        "read",
        "list",
        "count",
        "exists",
        "aggregate",
        "group_by",
        "subscribe",
        "tail",
        "download",
    }
)
_NON_PERSISTING_TARGETS = frozenset(
    {
        "delete",
        "clear",
        "bulk_delete",
        "close_stream",
        "close_session",
    }
)
_CREATE_LIKE_TARGETS = frozenset({"create", "bulk_create"})
_UPDATE_LIKE_TARGETS = frozenset({"update", "merge", "bulk_update", "bulk_merge"})
_REPLACE_LIKE_TARGETS = frozenset({"replace", "bulk_replace"})


def _storage_requires_input(storage: Any, alias: str) -> bool:
    if storage is None or alias == "update":
        return False
    if bool(getattr(storage, "primary_key", False)):
        if alias in {"replace", "delete"}:
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


def _supports_stored_shape(target: str) -> bool:
    lowered = str(target or "").lower()
    return lowered not in _READ_ONLY_TARGETS and lowered not in _NON_PERSISTING_TARGETS


def _is_input_enabled(io: Any, semantic_verbs: tuple[str, ...]) -> bool:
    in_verbs = set(getattr(io, "in_verbs", ()) or ())
    return any(name in in_verbs for name in semantic_verbs)


def _is_paired_enabled(io: Any, semantic_verbs: tuple[str, ...]) -> bool:
    cfg = getattr(io, "_paired", None)
    if cfg is None:
        return False
    paired_verbs = set(getattr(cfg, "verbs", ()) or ())
    return any(name in paired_verbs for name in semantic_verbs)


def _include_in_stored_schema(
    *,
    spec: Any,
    io: Any,
    storage: Any,
    semantic_verbs: tuple[str, ...],
    target: str,
) -> bool:
    lowered = str(target or "").lower()
    if storage is None or not _supports_stored_shape(lowered):
        return False
    if _is_input_enabled(io, semantic_verbs) or _is_paired_enabled(io, semantic_verbs):
        return True
    if lowered in _CREATE_LIKE_TARGETS or lowered in _UPDATE_LIKE_TARGETS:
        return True
    if lowered in _REPLACE_LIKE_TARGETS:
        return True
    return False


def _stored_required(storage: Any, spec: Any, target: str, *, derived: bool) -> bool:
    lowered = str(target or "").lower()
    if lowered in _UPDATE_LIKE_TARGETS:
        return False
    if lowered in _NON_PERSISTING_TARGETS or lowered in _READ_ONLY_TARGETS:
        return False
    if derived:
        return True
    return not bool(getattr(storage, "nullable", True)) and not _storage_has_server_default(
        spec,
        storage,
    )


def compile_opview_from_specs(specs: Mapping[str, Any], sp: Any) -> OpView:
    """Build a basic OpView from collected specs when no app/model is present."""
    alias = str(getattr(sp, "alias", "") or "")
    target = str(getattr(sp, "target", alias) or alias)
    semantic_verbs = tuple(
        dict.fromkeys(
            name
            for name in (alias, target)
            if isinstance(name, str) and name
        )
    )

    in_fields: list[str] = []
    out_fields: list[str] = []
    stored_fields: list[str] = []
    by_field_in: Dict[str, Dict[str, object]] = {}
    by_field_out: Dict[str, Dict[str, object]] = {}
    by_field_stored: Dict[str, Dict[str, object]] = {}
    required_from_client: list[str] = []
    to_stored_transforms: Dict[str, Any] = {}

    for name, spec in specs.items():
        io = getattr(spec, "io", None)
        fs = getattr(spec, "field", None)
        storage = getattr(spec, "storage", None)
        in_verbs = set(getattr(io, "in_verbs", ()) or ())
        out_verbs = set(getattr(io, "out_verbs", ()) or ())

        if any(name in in_verbs for name in semantic_verbs):
            in_fields.append(name)
            meta: Dict[str, object] = {"in_enabled": True}
            if storage is None:
                meta["virtual"] = True
            py_type = getattr(fs, "py_type", None)
            if py_type is not None and py_type is not Any:
                meta["py_type"] = py_type
            constraints = getattr(fs, "constraints", {}) or {}
            if isinstance(constraints, Mapping):
                max_length = constraints.get("max_length")
                if isinstance(max_length, int) and max_length > 0:
                    meta["max_length"] = max_length
            default_factory = getattr(spec, "default_factory", None)
            if callable(default_factory):
                meta["default_factory"] = default_factory
            alias_in = getattr(io, "alias_in", None)
            if alias_in:
                meta["alias_in"] = alias_in
            header_in = getattr(io, "header_in", None)
            if header_in:
                meta["header_in"] = header_in
                meta["header_required_in"] = bool(
                    getattr(io, "header_required_in", False)
                )
            required = bool(
                (fs and any(name in getattr(fs, "required_in", ()) for name in semantic_verbs))
                or _storage_requires_input(storage, target)
            )
            meta["required"] = required
            base_nullable = (
                True if storage is None else getattr(storage, "nullable", True)
            )
            meta["nullable"] = base_nullable
            meta["coerce"] = True
            by_field_in[name] = meta

        if any(name in out_verbs for name in semantic_verbs):
            out_fields.append(name)
            meta_out: Dict[str, object] = {}
            alias_out = getattr(io, "alias_out", None)
            if alias_out:
                meta_out["alias_out"] = alias_out
            if storage is None:
                meta_out["virtual"] = True
            py_type = getattr(getattr(fs, "py_type", None), "__name__", None)
            if py_type:
                meta_out["py_type"] = py_type
            by_field_out[name] = meta_out

        if _include_in_stored_schema(
            spec=spec,
            io=io,
            storage=storage,
            semantic_verbs=semantic_verbs,
            target=target,
        ):
            stored_fields.append(name)
            input_enabled = _is_input_enabled(io, semantic_verbs)
            paired_enabled = _is_paired_enabled(io, semantic_verbs)
            server_default = _storage_has_server_default(spec, storage)
            py_type = getattr(fs, "py_type", None)
            if py_type is None or py_type is Any:
                py_type = _storage_python_type(getattr(storage, "type_", None))
            else:
                py_type = _normalize_py_type(py_type)
            stored_meta: Dict[str, object] = {
                "nullable": bool(getattr(storage, "nullable", True)),
                "from_client": input_enabled,
                "required_from_client": bool(
                    input_enabled and _storage_requires_input(storage, target)
                ),
                "server_default": server_default,
            }
            if py_type is not Any:
                stored_meta["py_type"] = py_type
            constraints = getattr(fs, "constraints", {}) or {}
            if isinstance(constraints, Mapping):
                max_length = constraints.get("max_length")
                if isinstance(max_length, int) and max_length > 0:
                    stored_meta["max_length"] = max_length

            transform = getattr(getattr(storage, "transform", None), "to_stored", None)
            if callable(transform):
                to_stored_transforms[name] = transform

            derived = paired_enabled or callable(transform)
            stored_meta["derived"] = derived
            stored_meta["required"] = _stored_required(
                storage,
                spec,
                target,
                derived=derived,
            )
            if stored_meta["required_from_client"]:
                required_from_client.append(name)
            by_field_stored[name] = stored_meta

    schema_in = SchemaIn(
        fields=tuple(sorted(in_fields)),
        by_field={field: by_field_in.get(field, {}) for field in sorted(in_fields)},
    )
    schema_out = SchemaOut(
        fields=tuple(sorted(out_fields)),
        by_field={field: by_field_out.get(field, {}) for field in sorted(out_fields)},
        expose=tuple(sorted(out_fields)),
    )
    stored_fields_sorted = tuple(sorted(stored_fields))
    schema_stored = (
        SchemaStored(
            fields=stored_fields_sorted,
            by_field={
                field: by_field_stored.get(field, {})
                for field in stored_fields_sorted
            },
            required_from_client=tuple(sorted(required_from_client)),
        )
        if stored_fields_sorted
        else None
    )
    paired_index: Dict[str, Dict[str, object]] = {}
    for field, col in specs.items():
        io = getattr(col, "io", None)
        cfg = getattr(io, "_paired", None)
        if cfg and any(name in getattr(cfg, "verbs", ()) for name in semantic_verbs):  # type: ignore[attr-defined]
            field_spec = getattr(col, "field", None)
            max_length = None
            if field_spec is not None:
                max_length = getattr(
                    getattr(field_spec, "constraints", {}),
                    "get",
                    lambda k, d=None: None,
                )("max_length")
            paired_index[field] = {
                "alias": cfg.alias,
                "gen": cfg.gen,
                "store": cfg.store,
                "mask_last": cfg.mask_last,
                "max_length": max_length,
            }

    return OpView(
        schema_in=schema_in,
        schema_out=schema_out,
        paired_index=paired_index,
        virtual_producers={},
        to_stored_transforms=to_stored_transforms,
        refresh_hints=(),
        schema_stored=schema_stored,
    )
