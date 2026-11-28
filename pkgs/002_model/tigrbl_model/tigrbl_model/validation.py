"""Annotation-driven runtime validation used by the model compiler."""

from __future__ import annotations

import collections.abc
import re
import types
from dataclasses import fields as dataclass_fields, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import (
    Annotated,
    Any,
    ForwardRef,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from uuid import UUID

from .errors import ErrorDetails, ValidationError
from .fields import FieldInfo


class ValidationIssue(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        value: Any,
        loc: tuple[str | int, ...],
        context: dict[str, Any] | None = None,
    ) -> None:
        self.details = ErrorDetails(code, loc, message, value, context)
        super().__init__(message)


def _issue(
    code: str,
    message: str,
    value: Any,
    loc: tuple[str | int, ...],
    context: dict[str, Any] | None = None,
) -> ValidationIssue:
    return ValidationIssue(code, message, value, loc, context)


def _metadata_constraints(metadata: tuple[Any, ...], field: FieldInfo) -> FieldInfo:
    for item in metadata:
        for name in (
            "gt",
            "ge",
            "lt",
            "le",
            "multiple_of",
            "min_length",
            "max_length",
            "pattern",
        ):
            value = getattr(item, name, None)
            if value is not None:
                setattr(field, name, value)
    return field


def _apply_constraints(
    value: Any, field: FieldInfo, loc: tuple[str | int, ...]
) -> Any:
    checks = (
        ("gt", field.gt, lambda left, right: left > right, "greater_than"),
        ("ge", field.ge, lambda left, right: left >= right, "greater_than_equal"),
        ("lt", field.lt, lambda left, right: left < right, "less_than"),
        ("le", field.le, lambda left, right: left <= right, "less_than_equal"),
    )
    for label, boundary, predicate, code in checks:
        if boundary is not None:
            try:
                valid = predicate(value, boundary)
            except TypeError:
                valid = False
            if not valid:
                raise _issue(
                    code,
                    f"Input should be {label.replace('_', ' ')} {boundary}",
                    value,
                    loc,
                    {label: boundary},
                )
    if field.multiple_of is not None and value % field.multiple_of != 0:
        raise _issue(
            "multiple_of",
            f"Input should be a multiple of {field.multiple_of}",
            value,
            loc,
            {"multiple_of": field.multiple_of},
        )
    try:
        length = len(value)
    except TypeError:
        length = None
    minimum = field.min_length if field.min_length is not None else field.min_items
    maximum = field.max_length if field.max_length is not None else field.max_items
    if minimum is not None and (length is None or length < minimum):
        raise _issue(
            "too_short",
            f"Value should have at least {minimum} item(s)",
            value,
            loc,
            {"min_length": minimum},
        )
    if maximum is not None and (length is None or length > maximum):
        raise _issue(
            "too_long",
            f"Value should have at most {maximum} item(s)",
            value,
            loc,
            {"max_length": maximum},
        )
    if field.pattern is not None and (
        not isinstance(value, str) or re.search(field.pattern, value) is None
    ):
        raise _issue(
            "string_pattern_mismatch",
            f"String should match pattern {field.pattern!r}",
            value,
            loc,
            {"pattern": str(field.pattern)},
        )
    return value


def validate_value(
    annotation: Any,
    value: Any,
    *,
    field: FieldInfo | None = None,
    loc: tuple[str | int, ...] = (),
    strict: bool = False,
    arbitrary_types_allowed: bool = False,
) -> Any:
    """Validate and coerce a value against a Python type annotation."""

    field = field or FieldInfo(annotation=annotation)
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Annotated:
        base, *metadata = args
        field = _metadata_constraints(tuple(metadata), field)
        return validate_value(
            base,
            value,
            field=field,
            loc=loc,
            strict=strict,
            arbitrary_types_allowed=arbitrary_types_allowed,
        )
    if annotation in (Any, object) or annotation is None:
        return _apply_constraints(value, field, loc)
    if isinstance(annotation, TypeVar):
        if annotation.__constraints__:
            annotation = Union[annotation.__constraints__]  # type: ignore[index]
        else:
            annotation = annotation.__bound__ or Any
        return validate_value(
            annotation,
            value,
            field=field,
            loc=loc,
            strict=strict,
            arbitrary_types_allowed=arbitrary_types_allowed,
        )
    if isinstance(annotation, (ForwardRef, str)):
        raise _issue(
            "class_not_fully_defined",
            f"Unresolved annotation {annotation!r}; call model_rebuild()",
            value,
            loc,
        )
    if annotation is type(None):
        if value is None:
            return None
        raise _issue("none_required", "Input should be None", value, loc)

    if origin in (Union, types.UnionType):
        if type(None) in args:
            if value is None:
                return None
            non_null = tuple(choice for choice in args if choice is not type(None))
            if len(non_null) == 1:
                return validate_value(
                    non_null[0],
                    value,
                    field=field,
                    loc=loc,
                    strict=strict,
                    arbitrary_types_allowed=arbitrary_types_allowed,
                )
        failures: list[ErrorDetails] = []
        for choice in args:
            try:
                return validate_value(
                    choice,
                    value,
                    field=field,
                    loc=loc,
                    strict=strict,
                    arbitrary_types_allowed=arbitrary_types_allowed,
                )
            except ValidationIssue as exc:
                failures.append(exc.details)
            except ValidationError as exc:
                failures.extend(
                    ErrorDetails(
                        item["type"], tuple(item["loc"]), item["msg"], item.get("input")
                    )
                    for item in exc.errors(include_url=False)
                )
        names = ", ".join(getattr(choice, "__name__", str(choice)) for choice in args)
        raise _issue(
            "union_tag_invalid",
            f"Input should match one of: {names}",
            value,
            loc,
            {"errors": [item.as_dict(include_url=False) for item in failures]},
        )

    if origin is Literal:
        if value in args and type(value) in {type(item) for item in args}:
            return value
        expected = ", ".join(repr(item) for item in args)
        raise _issue(
            "literal_error", f"Input should be {expected}", value, loc, {"expected": expected}
        )

    if origin in (list, set, frozenset, collections.abc.Sequence):
        if isinstance(value, (str, bytes, bytearray, dict)) or not isinstance(
            value, collections.abc.Iterable
        ):
            raise _issue("list_type", "Input should be a valid sequence", value, loc)
        item_type = args[0] if args else Any
        converted = [
            validate_value(
                item_type,
                item,
                loc=(*loc, index),
                strict=strict,
                arbitrary_types_allowed=arbitrary_types_allowed,
            )
            for index, item in enumerate(value)
        ]
        result = set(converted) if origin is set else frozenset(converted) if origin is frozenset else converted
        return _apply_constraints(result, field, loc)

    if origin is tuple:
        if isinstance(value, (str, bytes, bytearray, dict)) or not isinstance(
            value, collections.abc.Iterable
        ):
            raise _issue("tuple_type", "Input should be a valid tuple", value, loc)
        source = tuple(value)
        if len(args) == 2 and args[1] is Ellipsis:
            converted = tuple(
                validate_value(
                    args[0],
                    item,
                    loc=(*loc, index),
                    strict=strict,
                    arbitrary_types_allowed=arbitrary_types_allowed,
                )
                for index, item in enumerate(source)
            )
        elif args:
            if len(source) != len(args):
                raise _issue(
                    "tuple_length",
                    f"Tuple should have {len(args)} items",
                    value,
                    loc,
                )
            converted = tuple(
                validate_value(
                    item_type,
                    item,
                    loc=(*loc, index),
                    strict=strict,
                    arbitrary_types_allowed=arbitrary_types_allowed,
                )
                for index, (item_type, item) in enumerate(zip(args, source))
            )
        else:
            converted = source
        return _apply_constraints(converted, field, loc)

    if origin in (dict, collections.abc.Mapping):
        if not isinstance(value, collections.abc.Mapping):
            raise _issue("dict_type", "Input should be a valid mapping", value, loc)
        key_type, value_type = args if len(args) == 2 else (Any, Any)
        converted = {}
        for key, item in value.items():
            converted_key = validate_value(
                key_type,
                key,
                loc=(*loc, "[key]"),
                strict=strict,
                arbitrary_types_allowed=arbitrary_types_allowed,
            )
            converted[converted_key] = validate_value(
                value_type,
                item,
                loc=(*loc, key),
                strict=strict,
                arbitrary_types_allowed=arbitrary_types_allowed,
            )
        return _apply_constraints(converted, field, loc)

    if origin in (type, collections.abc.Callable):
        if origin is type:
            if not isinstance(value, type):
                raise _issue("is_type", "Input should be a type", value, loc)
            if args and args[0] not in (Any, object) and not issubclass(value, args[0]):
                raise _issue("is_subclass_of", f"Input should subclass {args[0]}", value, loc)
            return value
        if not callable(value):
            raise _issue("callable_type", "Input should be callable", value, loc)
        return value

    if isinstance(annotation, type) and hasattr(annotation, "model_validate"):
        try:
            return annotation.model_validate(value, strict=strict)
        except ValidationError:
            raise
        except Exception as exc:
            raise _issue("model_type", str(exc), value, loc) from exc

    if isinstance(annotation, type) and is_dataclass(annotation):
        if isinstance(value, annotation):
            return value
        if not isinstance(value, collections.abc.Mapping):
            raise _issue("dataclass_type", "Input should be a mapping", value, loc)
        values: dict[str, Any] = {}
        errors: list[ErrorDetails] = []
        for item in dataclass_fields(annotation):
            if item.name not in value:
                continue
            try:
                values[item.name] = validate_value(
                    item.type,
                    value[item.name],
                    loc=(*loc, item.name),
                    strict=strict,
                    arbitrary_types_allowed=arbitrary_types_allowed,
                )
            except ValidationIssue as exc:
                errors.append(exc.details)
        if errors:
            raise ValidationError(annotation.__name__, errors)
        return annotation(**values)

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        if isinstance(value, annotation):
            return value
        try:
            return annotation(value)
        except (ValueError, TypeError) as exc:
            raise _issue("enum", f"Input should be a valid {annotation.__name__}", value, loc) from exc

    if annotation is bool:
        if isinstance(value, bool):
            return value
        if not strict:
            if value in (1, "1", "true", "True", "yes", "on"):
                return True
            if value in (0, "0", "false", "False", "no", "off"):
                return False
        raise _issue("bool_parsing", "Input should be a valid boolean", value, loc)
    if annotation is int:
        if isinstance(value, int) and not isinstance(value, bool):
            result = value
        elif not strict and isinstance(value, float) and value.is_integer():
            result = int(value)
        elif not strict and isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value):
            result = int(value)
        else:
            raise _issue("int_parsing", "Input should be a valid integer", value, loc)
        return _apply_constraints(result, field, loc)
    if annotation is float:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result = float(value)
        elif not strict and isinstance(value, str):
            try:
                result = float(value)
            except ValueError as exc:
                raise _issue("float_parsing", "Input should be a valid number", value, loc) from exc
        else:
            raise _issue("float_type", "Input should be a valid number", value, loc)
        return _apply_constraints(result, field, loc)
    if annotation is str:
        if not isinstance(value, str):
            raise _issue("string_type", "Input should be a valid string", value, loc)
        return _apply_constraints(value, field, loc)
    if annotation is bytes:
        if isinstance(value, bytes):
            return value
        if not strict and isinstance(value, (str, bytearray)):
            return value.encode() if isinstance(value, str) else bytes(value)
        raise _issue("bytes_type", "Input should be valid bytes", value, loc)

    scalar_parsers = {
        UUID: UUID,
        Decimal: Decimal,
        Path: Path,
        datetime: datetime.fromisoformat,
        date: date.fromisoformat,
        time: time.fromisoformat,
    }
    if annotation in scalar_parsers:
        if isinstance(value, annotation):
            return value
        if strict or not isinstance(value, str):
            raise _issue(
                f"{annotation.__name__}_type",
                f"Input should be a valid {annotation.__name__}",
                value,
                loc,
            )
        try:
            return scalar_parsers[annotation](value)
        except (ValueError, TypeError) as exc:
            raise _issue(
                f"{annotation.__name__}_parsing",
                f"Input should be a valid {annotation.__name__}",
                value,
                loc,
            ) from exc

    if isinstance(annotation, type):
        if isinstance(value, annotation):
            return value
        if arbitrary_types_allowed:
            raise _issue(
                "is_instance_of", f"Input should be an instance of {annotation.__name__}", value, loc
            )
        raise _issue(
            "schema_for_unknown_type",
            f"No validator is defined for {annotation!r}; enable arbitrary_types_allowed",
            value,
            loc,
        )

    return _apply_constraints(value, field, loc)


__all__ = ["ValidationIssue", "validate_value"]
