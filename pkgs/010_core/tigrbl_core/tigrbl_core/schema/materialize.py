"""Schema-owned ingress value materialization."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any, Callable

from pydantic import AfterValidator, Field, TypeAdapter


def validated_type(
    annotation: type, validator: Callable[[Any], Any], **constraints: Any
) -> Any:
    """Build a field annotation that validates a parsed value with a callable."""
    return Annotated[annotation, Field(**constraints), AfterValidator(validator)]


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


__all__ = ["_materialize_field_value", "validated_type"]
