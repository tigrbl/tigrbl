"""Draft 2020-12 JSON Schema generation for Tigrbl models."""

from __future__ import annotations

import collections.abc
import types
from dataclasses import MISSING, fields as dataclass_fields, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Literal, Union, get_args, get_origin
from uuid import UUID

from .fields import FieldInfo, PydanticUndefined
from .serialization import serialize_value


class SchemaContext:
    def __init__(self, *, ref_template: str, by_alias: bool, mode: str) -> None:
        self.ref_template = ref_template
        self.by_alias = by_alias
        self.mode = mode
        self.defs: dict[str, dict[str, Any]] = {}
        self.building: set[type] = set()

    def ref(self, model: type) -> dict[str, str]:
        return {"$ref": self.ref_template.format(model=model.__name__)}


def _apply_field_schema(schema: dict[str, Any], field: FieldInfo) -> dict[str, Any]:
    if field.title:
        schema["title"] = field.title
    if field.description:
        schema["description"] = field.description
    if field.examples:
        schema["examples"] = field.examples
    mappings = {
        "exclusiveMinimum": field.gt,
        "minimum": field.ge,
        "exclusiveMaximum": field.lt,
        "maximum": field.le,
        "multipleOf": field.multiple_of,
        "minLength": field.min_length,
        "maxLength": field.max_length,
        "pattern": str(field.pattern) if field.pattern is not None else None,
        "minItems": field.min_items,
        "maxItems": field.max_items,
    }
    schema.update({key: value for key, value in mappings.items() if value is not None})
    if not field.is_required() and field.default is not PydanticUndefined:
        try:
            schema["default"] = serialize_value(field.default, mode="json")
        except TypeError:
            pass
    if isinstance(field.json_schema_extra, dict):
        schema.update(field.json_schema_extra)
    elif callable(field.json_schema_extra):
        field.json_schema_extra(schema)
    return schema


def _model_definition(model: type, context: SchemaContext) -> dict[str, Any]:
    if model in context.building:
        return context.ref(model)
    context.building.add(model)
    try:
        if getattr(model, "__root_model__", False):
            root = model.model_fields["root"]
            result = _schema_for(root.annotation, context, root)
            result.setdefault("title", model.__name__)
        else:
            properties: dict[str, Any] = {}
            required: list[str] = []
            for name, field in model.model_fields.items():
                output_name = (
                    field.schema_name(name, mode=context.mode)
                    if context.by_alias
                    else name
                )
                field_schema = _schema_for(field.annotation, context, field)
                if "$ref" not in field_schema:
                    field_schema.setdefault(
                        "title", output_name.replace("_", " ").title()
                    )
                properties[output_name] = field_schema
                if field.is_required():
                    required.append(output_name)
            result = {
                "properties": properties,
                "title": model.__name__,
                "type": "object",
            }
            if required:
                result["required"] = required
            if model.model_config.get("extra") == "forbid":
                result["additionalProperties"] = False
        extra = model.model_config.get("json_schema_extra")
        if isinstance(extra, dict):
            result.update(extra)
        elif callable(extra):
            extra(result)
        return result
    finally:
        context.building.remove(model)


def _schema_for(annotation: Any, context: SchemaContext, field: FieldInfo | None = None) -> dict[str, Any]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Annotated:
        annotation, *metadata = args
        if field is None:
            field = FieldInfo(annotation=annotation)
        for item in metadata:
            for name in ("gt", "ge", "lt", "le", "multiple_of", "min_length", "max_length"):
                value = getattr(item, name, None)
                if value is not None:
                    setattr(field, name, value)
        return _schema_for(annotation, context, field)
    if annotation in (Any, object):
        schema: dict[str, Any] = {}
    elif annotation is type(None):
        schema = {"type": "null"}
    elif origin in (Union, types.UnionType):
        schema = {"anyOf": [_schema_for(item, context) for item in args]}
    elif origin is Literal:
        schema = {"enum": list(args)}
        types_seen = {type(item) for item in args}
        if len(types_seen) == 1:
            schema.update(_schema_for(next(iter(types_seen)), context))
    elif origin in (list, set, frozenset, collections.abc.Sequence):
        schema = {"type": "array", "items": _schema_for(args[0] if args else Any, context)}
        if origin in (set, frozenset):
            schema["uniqueItems"] = True
    elif origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            schema = {"type": "array", "items": _schema_for(args[0], context)}
        elif args:
            schema = {
                "type": "array",
                "prefixItems": [_schema_for(item, context) for item in args],
                "minItems": len(args),
                "maxItems": len(args),
            }
        else:
            schema = {"type": "array"}
    elif origin in (dict, collections.abc.Mapping):
        value_type = args[1] if len(args) == 2 else Any
        schema = {"type": "object", "additionalProperties": _schema_for(value_type, context)}
    elif isinstance(annotation, type) and hasattr(annotation, "model_fields"):
        annotation.model_rebuild(raise_errors=False)
        name = annotation.__name__
        if name not in context.defs and annotation not in context.building:
            context.defs[name] = _model_definition(annotation, context)
        schema = context.ref(annotation)
    elif isinstance(annotation, type) and is_dataclass(annotation):
        properties = {}
        required = []
        for item in dataclass_fields(annotation):
            properties[item.name] = _schema_for(item.type, context)
            if item.default is MISSING and item.default_factory is MISSING:
                required.append(item.name)
        schema = {"type": "object", "properties": properties, "title": annotation.__name__}
        if required:
            schema["required"] = required
    elif isinstance(annotation, type) and issubclass(annotation, Enum):
        values = [item.value for item in annotation]
        schema = {"enum": values, "title": annotation.__name__}
        if values:
            schema.update(_schema_for(type(values[0]), context))
    else:
        mapping: dict[Any, dict[str, Any]] = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            bytes: {"type": "string", "format": "binary"},
            UUID: {"type": "string", "format": "uuid"},
            datetime: {"type": "string", "format": "date-time"},
            date: {"type": "string", "format": "date"},
            time: {"type": "string", "format": "time"},
            Decimal: {"anyOf": [{"type": "number"}, {"type": "string"}]},
            Path: {"type": "string", "format": "path"},
        }
        schema = dict(mapping.get(annotation, {}))
    return _apply_field_schema(schema, field) if field is not None else schema


def model_json_schema(
    model: type,
    *,
    by_alias: bool = True,
    ref_template: str = "#/$defs/{model}",
    mode: str = "validation",
) -> dict[str, Any]:
    """Generate a JSON Schema document for a compiled model class."""

    context = SchemaContext(ref_template=ref_template, by_alias=by_alias, mode=mode)
    schema = _model_definition(model, context)
    context.defs.pop(model.__name__, None)
    if context.defs:
        schema["$defs"] = context.defs
    return schema


__all__ = ["model_json_schema"]
