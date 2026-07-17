"""Field declarations and metadata."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field as dataclass_field
from typing import Any, Callable


class _UndefinedType:
    def __repr__(self) -> str:
        return "PydanticUndefined"

    def __copy__(self) -> "_UndefinedType":
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> "_UndefinedType":
        return self


PydanticUndefined = _UndefinedType()
Undefined = PydanticUndefined


@dataclass(frozen=True, slots=True)
class AliasChoices:
    """Ordered validation aliases; the first present alias wins."""

    choices: tuple[str, ...]

    def __init__(self, first: str, *choices: str):
        object.__setattr__(self, "choices", (first, *choices))


@dataclass(slots=True)
class FieldInfo:
    """Runtime metadata for one declared model field."""

    annotation: Any = Any
    default: Any = PydanticUndefined
    default_factory: Callable[[], Any] | None = None
    alias: str | None = None
    validation_alias: str | AliasChoices | None = None
    serialization_alias: str | None = None
    title: str | None = None
    description: str | None = None
    examples: list[Any] | None = None
    json_schema_extra: dict[str, Any] | Callable[[dict[str, Any]], None] | None = None
    gt: Any = None
    ge: Any = None
    lt: Any = None
    le: Any = None
    multiple_of: Any = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | re.Pattern[str] | None = None
    min_items: int | None = None
    max_items: int | None = None
    exclude: bool = False
    repr: bool = True
    metadata: list[Any] = dataclass_field(default_factory=list)

    def is_required(self) -> bool:
        return self.default is PydanticUndefined and self.default_factory is None

    def get_default(self, *, call_default_factory: bool = False) -> Any:
        if self.default_factory is not None:
            return self.default_factory() if call_default_factory else None
        if self.default is PydanticUndefined:
            return PydanticUndefined
        return copy.deepcopy(self.default)

    def validation_names(self, name: str) -> tuple[str, ...]:
        alias = self.validation_alias or self.alias
        if isinstance(alias, AliasChoices):
            return alias.choices
        if isinstance(alias, str):
            return (alias,)
        return (name,)

    def serialization_name(self, name: str) -> str:
        return self.serialization_alias or self.alias or name

    def schema_name(self, name: str, *, mode: str) -> str:
        if mode == "serialization":
            return self.serialization_name(name)
        alias = self.validation_alias or self.alias
        if isinstance(alias, AliasChoices):
            return alias.choices[0]
        return alias if isinstance(alias, str) else name


def Field(
    default: Any = PydanticUndefined,
    *,
    default_factory: Callable[[], Any] | None = None,
    alias: str | None = None,
    validation_alias: str | AliasChoices | None = None,
    serialization_alias: str | None = None,
    title: str | None = None,
    description: str | None = None,
    examples: list[Any] | None = None,
    json_schema_extra: dict[str, Any] | Callable[[dict[str, Any]], None] | None = None,
    gt: Any = None,
    ge: Any = None,
    lt: Any = None,
    le: Any = None,
    multiple_of: Any = None,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | re.Pattern[str] | None = None,
    min_items: int | None = None,
    max_items: int | None = None,
    exclude: bool = False,
    repr: bool = True,
    **extra: Any,
) -> FieldInfo:
    """Declare field defaults, aliases, constraints, and schema metadata."""

    if default is Ellipsis:
        default = PydanticUndefined
    if "regex" in extra:
        from .errors import ModelUserError

        raise ModelUserError(
            "`regex` is removed; use `pattern` instead",
            code="removed-kwargs",
        )
    if "unique_items" in extra:
        from .errors import ModelUserError

        raise ModelUserError(
            "`unique_items` is removed; use a set annotation instead",
            code="removed-kwargs",
        )
    if default is not PydanticUndefined and default_factory is not None:
        raise TypeError("cannot specify both default and default_factory")
    info = FieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        validation_alias=validation_alias,
        serialization_alias=serialization_alias,
        title=title,
        description=description,
        examples=examples,
        json_schema_extra=json_schema_extra,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        min_items=min_items,
        max_items=max_items,
        exclude=exclude,
        repr=repr,
    )
    info.metadata.extend((key, value) for key, value in extra.items())
    return info


__all__ = [
    "AliasChoices",
    "Field",
    "FieldInfo",
    "PydanticUndefined",
    "Undefined",
]
