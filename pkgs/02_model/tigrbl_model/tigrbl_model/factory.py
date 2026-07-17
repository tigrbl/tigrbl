"""Dynamic model construction."""

from __future__ import annotations

import sys
from typing import Any

from .config import ConfigDict
from .fields import FieldInfo, PydanticUndefined
from .model import Model


def create_model(
    model_name: str,
    *,
    __config__: ConfigDict | dict[str, Any] | None = None,
    __base__: type[Model] | tuple[type[Model], ...] | None = None,
    __module__: str | None = None,
    __validators__: dict[str, Any] | None = None,
    __doc__: str | None = None,
    **field_definitions: Any,
) -> type[Model]:
    """Create a model class from `(annotation, default)` field definitions."""

    bases = __base__ or Model
    if not isinstance(bases, tuple):
        bases = (bases,)
    annotations: dict[str, Any] = {}
    namespace: dict[str, Any] = {
        "__annotations__": annotations,
        "__module__": __module__ or sys._getframe(1).f_globals.get("__name__", "__main__"),
    }
    if __doc__ is not None:
        namespace["__doc__"] = __doc__
    if __config__ is not None:
        namespace["model_config"] = ConfigDict(__config__)
    namespace.update(__validators__ or {})
    for name, definition in field_definitions.items():
        if isinstance(definition, tuple) and len(definition) == 2:
            annotation, default = definition
        else:
            annotation, default = definition, PydanticUndefined
        annotations[name] = annotation
        if default is Ellipsis:
            default = PydanticUndefined
        if isinstance(default, FieldInfo):
            namespace[name] = default
        elif default is not PydanticUndefined:
            namespace[name] = default
    return type(model_name, bases, namespace)


__all__ = ["create_model"]
