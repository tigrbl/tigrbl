"""Internal helper utilities for schema building."""

from __future__ import annotations

from types import UnionType
from typing import (
    Mapping,
    Any,
    Dict,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import Field


def _bool(x: Any) -> bool:
    try:
        return bool(x)
    except Exception:  # pragma: no cover
        return False


def _normalize_py_type(py_t: type | Any) -> type | Any:
    """Normalize dynamic field type declarations for safe schema generation."""
    if isinstance(py_t, property):
        getter = py_t.fget
        if getter is None:
            return Any

        try:
            return _normalize_py_type(get_type_hints(getter).get("return", Any))
        except Exception:  # pragma: no cover
            return Any

    # ``typing.Union[..., <property object>]`` can appear when extras or
    # computed columns accidentally register a ``property`` INSTANCE in a type
    # declaration. Recursively normalize union members so we can safely rebuild
    # a pydantic-compatible annotation.
    origin = get_origin(py_t)
    if origin in (Union, UnionType):
        args = tuple(_normalize_py_type(arg) for arg in get_args(py_t))
        filtered = tuple(arg for arg in args if arg is not None)
        if not filtered:
            return Any
        rebuilt = filtered[0]
        for arg in filtered[1:]:
            rebuilt = rebuilt | arg
        return rebuilt

    return py_t


def _add_field(
    sink: Dict[str, Tuple[type, Field]],
    *,
    name: str,
    py_t: type | Any,
    field: Field | None = None,
) -> None:
    # ``property`` descriptors can leak into extras definitions when callers
    # register computed attributes directly (instead of their return type).
    # Pydantic cannot generate schemas for a raw property object, so degrade to
    # ``Any`` and let runtime serializers provide the concrete value.
    py_t = _normalize_py_type(py_t)
    sink[name] = (py_t, field if field is not None else Field(None))


def _python_type(col: Any) -> type | Any:
    try:
        return col.type.python_type
    except Exception:  # pragma: no cover
        return Any


def _storage_python_type(storage_type: Any) -> type | Any:
    """Resolve a StorageSpec type reference to a concrete Python type."""
    candidates = [storage_type]
    if isinstance(storage_type, type):
        try:
            candidates.append(storage_type())
        except Exception:  # pragma: no cover
            pass

    for candidate in candidates:
        try:
            py_t = _normalize_py_type(candidate.python_type)
        except Exception:
            continue
        if py_t is not Any:
            return py_t
    return Any


def _spec_python_type(spec: Any) -> Any:
    """Resolve a declared field annotation, including mapped-column specs."""
    annotation = getattr(getattr(spec, "field", None), "py_type", None)
    if annotation is not None and annotation is not Any:
        return _normalize_py_type(annotation)
    return _storage_python_type(getattr(getattr(spec, "storage", None), "type_", None))


def _input_selector_entries(
    specs: Mapping[str, Any], target: str
) -> Dict[str, Dict[str, Any]]:
    """Describe operation identifiers as schema inputs, not writable columns."""
    if target not in {
        "read",
        "exists",
        "update",
        "replace",
        "merge",
        "delete",
        "bulk_update",
        "bulk_replace",
        "bulk_merge",
        "bulk_delete",
    }:
        return {}
    primary = [
        (name, spec)
        for name, spec in specs.items()
        if bool(getattr(getattr(spec, "storage", None), "primary_key", False))
    ]
    if len(primary) != 1:
        return {}
    name, spec = primary[0]
    annotation = _spec_python_type(spec)
    entries = {
        name: {
            "py_type": annotation,
            "selector": True,
            "required": False,
            "nullable": False,
            "in_enabled": False,
        }
    }
    if target == "bulk_delete":
        entries["ids"] = {
            "py_type": list[annotation],
            "selector_collection": True,
            "required": False,
            "nullable": False,
            "in_enabled": False,
        }
    return entries


def _is_required(col: Any, verb: str) -> bool:
    """Decide if a column should be required for the given verb."""
    if getattr(col, "primary_key", False):
        if verb in {"update", "replace", "delete"}:
            return True
        auto = getattr(col, "autoincrement", False)
        if auto not in (False, None) or getattr(col, "identity", None) is not None:
            return False
    if verb == "update":
        return False
    is_nullable = bool(getattr(col, "nullable", True))
    has_default = (getattr(col, "default", None) is not None) or (
        getattr(col, "server_default", None) is not None
    )
    return not is_nullable and not has_default


__all__ = [
    "_bool",
    "_add_field",
    "_normalize_py_type",
    "_python_type",
    "_storage_python_type",
    "_spec_python_type",
    "_input_selector_entries",
    "_is_required",
]
