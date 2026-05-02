from __future__ import annotations

from typing import Any, Dict, Mapping

from .models import OpView, SchemaIn, SchemaOut


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


def compile_opview_from_specs(specs: Mapping[str, Any], sp: Any) -> OpView:
    """Build a basic OpView from collected specs when no app/model is present."""
    alias = getattr(sp, "alias", "")

    in_fields: list[str] = []
    out_fields: list[str] = []
    by_field_in: Dict[str, Dict[str, object]] = {}
    by_field_out: Dict[str, Dict[str, object]] = {}

    for name, spec in specs.items():
        io = getattr(spec, "io", None)
        fs = getattr(spec, "field", None)
        storage = getattr(spec, "storage", None)
        in_verbs = set(getattr(io, "in_verbs", ()) or ())
        out_verbs = set(getattr(io, "out_verbs", ()) or ())

        if alias in in_verbs:
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
                (fs and alias in getattr(fs, "required_in", ()))
                or _storage_requires_input(storage, alias)
            )
            meta["required"] = required
            base_nullable = (
                True if storage is None else getattr(storage, "nullable", True)
            )
            meta["nullable"] = base_nullable
            meta["coerce"] = True
            by_field_in[name] = meta

        if alias in out_verbs:
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

    schema_in = SchemaIn(
        fields=tuple(sorted(in_fields)),
        by_field={field: by_field_in.get(field, {}) for field in sorted(in_fields)},
    )
    schema_out = SchemaOut(
        fields=tuple(sorted(out_fields)),
        by_field={field: by_field_out.get(field, {}) for field in sorted(out_fields)},
        expose=tuple(sorted(out_fields)),
    )
    paired_index: Dict[str, Dict[str, object]] = {}
    for field, col in specs.items():
        io = getattr(col, "io", None)
        cfg = getattr(io, "_paired", None)
        if cfg and alias in getattr(cfg, "verbs", ()):  # type: ignore[attr-defined]
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
        to_stored_transforms={},
        refresh_hints=(),
    )
