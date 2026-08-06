"""Schema-owned ingress value materialization."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import TypeAdapter


@lru_cache(maxsize=512)
def _adapter(annotation: Any) -> TypeAdapter[Any]:
    return TypeAdapter(annotation)


def _materialize_field_value(value: Any, annotation: Any) -> Any:
    """Validate one carrier value through its declared field annotation."""

    if annotation is None or annotation is Any:
        return value
    try:
        adapter = _adapter(annotation)
    except TypeError:
        adapter = TypeAdapter(annotation)
    return adapter.validate_python(value)


__all__ = ["_materialize_field_value"]
