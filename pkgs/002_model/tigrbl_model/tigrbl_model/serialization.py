"""Shared normalization for Python and wire-format serialization."""

from __future__ import annotations

import base64
from dataclasses import fields as dataclass_fields, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Literal
from uuid import UUID

SerializationMode = Literal["python", "json"]


def nested_selection(selection: Any, key: str | int) -> Any:
    if not isinstance(selection, dict):
        return None
    return selection.get(key, selection.get("__all__"))


def selected(selection: Any, key: str | int, *, default: bool) -> bool:
    if selection is None:
        return default
    if isinstance(selection, set):
        return key in selection
    if isinstance(selection, dict):
        return key in selection or "__all__" in selection
    return bool(selection)


def excluded(selection: Any, key: str | int) -> bool:
    if selection is None:
        return False
    if isinstance(selection, set):
        return key in selection
    if isinstance(selection, dict):
        marker = selection.get(key, selection.get("__all__", False))
        return marker is True or marker is Ellipsis
    return bool(selection)


def serialize_value(
    value: Any,
    *,
    mode: SerializationMode,
    include: Any = None,
    exclude: Any = None,
    by_alias: bool = False,
    exclude_none: bool = False,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    fallback: Callable[[Any], Any] | None = None,
) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return value.model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            fallback=fallback,
        )
    if is_dataclass(value) and not isinstance(value, type):
        result = {}
        for item in dataclass_fields(value):
            if not selected(include, item.name, default=include is None):
                continue
            if excluded(exclude, item.name):
                continue
            child = getattr(value, item.name)
            if exclude_none and child is None:
                continue
            result[item.name] = serialize_value(
                child,
                mode=mode,
                include=nested_selection(include, item.name),
                exclude=nested_selection(exclude, item.name),
                by_alias=by_alias,
                exclude_none=exclude_none,
                fallback=fallback,
            )
        return result
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            if not selected(include, key, default=include is None):
                continue
            if excluded(exclude, key) or (exclude_none and child is None):
                continue
            result[key] = serialize_value(
                child,
                mode=mode,
                include=nested_selection(include, key),
                exclude=nested_selection(exclude, key),
                by_alias=by_alias,
                exclude_none=exclude_none,
                fallback=fallback,
            )
        return result
    if isinstance(value, (list, tuple, set, frozenset)):
        converted = [
            serialize_value(
                child,
                mode=mode,
                include=nested_selection(include, index),
                exclude=nested_selection(exclude, index),
                by_alias=by_alias,
                exclude_none=exclude_none,
                fallback=fallback,
            )
            for index, child in enumerate(value)
            if selected(include, index, default=include is None)
            and not excluded(exclude, index)
            and not (exclude_none and child is None)
        ]
        if mode == "python" and isinstance(value, tuple):
            return tuple(converted)
        if mode == "python" and isinstance(value, set):
            return set(converted)
        if mode == "python" and isinstance(value, frozenset):
            return frozenset(converted)
        return converted
    if isinstance(value, Enum):
        return serialize_value(value.value, mode=mode, fallback=fallback)
    if isinstance(value, (UUID, Decimal, Path, datetime, date, time)):
        return value if mode == "python" else str(value)
    if isinstance(value, bytes):
        if mode == "python":
            return value
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(value).decode("ascii")
    if isinstance(value, type):
        return value if mode == "python" else f"{value.__module__}:{value.__qualname__}"
    if callable(value):
        return value if mode == "python" else f"{value.__module__}:{value.__qualname__}"
    if fallback is not None:
        return fallback(value)
    if mode == "python":
        return value
    raise TypeError(f"Unable to serialize value of type {type(value).__name__}")


def strip_toml_nulls(value: Any) -> Any:
    """Remove values TOML cannot represent, including null list members."""

    if isinstance(value, dict):
        return {key: strip_toml_nulls(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [strip_toml_nulls(item) for item in value if item is not None]
    return value


__all__ = ["excluded", "serialize_value", "strip_toml_nulls"]
