"""Aggregate Python, JSON, YAML, and TOML serialization capability."""

from __future__ import annotations

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Any, Callable, Literal
try:
    from typing import Self
except ImportError:  # pragma: no cover - Python 3.10 compatibility
    from typing_extensions import Self

from ..fields import PydanticUndefined
from ..serialization import excluded, nested_selection, selected, serialize_value
from .json import JsonMixin
from .toml import TomlMixin
from .yaml import YamlMixin


class SerdeMixin(JsonMixin, YamlMixin, TomlMixin):
    def model_dump(
        self,
        *,
        mode: Literal["python", "json"] = "python",
        include: Any = None,
        exclude: Any = None,
        context: Any = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: Any = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        del context, round_trip, warnings, serialize_as_any
        by_alias = bool(by_alias)
        model_fields = getattr(type(self), "model_fields", None)
        fields_set = getattr(self, "model_fields_set", set())
        if isinstance(model_fields, dict):
            source = ((name, info, getattr(self, name, PydanticUndefined)) for name, info in model_fields.items())
        elif is_dataclass(self):
            source = (
                (item.name, None, getattr(self, item.name, PydanticUndefined))
                for item in dataclass_fields(self)
            )
        else:
            source = (
                (name, None, value)
                for name, value in vars(self).items()
                if not name.startswith("_")
            )
        result: dict[str, Any] = {}
        for name, info, value in source:
            if value is PydanticUndefined or (info is not None and info.exclude):
                continue
            if not selected(include, name, default=include is None):
                continue
            if excluded(exclude, name):
                continue
            if exclude_unset and name not in fields_set:
                continue
            if exclude_none and value is None:
                continue
            if exclude_defaults and info is not None and not info.is_required():
                default = info.get_default(call_default_factory=True)
                if value == default:
                    continue
            output_name = info.serialization_name(name) if by_alias and info is not None else name
            result[output_name] = serialize_value(
                value,
                mode=mode,
                include=nested_selection(include, name),
                exclude=nested_selection(exclude, name),
                by_alias=by_alias,
                exclude_none=exclude_none,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                fallback=fallback,
            )
        extra = getattr(self, "__model_extra__", None)
        if extra:
            result.update(
                serialize_value(
                    extra,
                    mode=mode,
                    by_alias=by_alias,
                    exclude_none=exclude_none,
                    fallback=fallback,
                )
            )
        return result

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: str | None = None,
        from_attributes: bool | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        del context, by_alias, by_name
        if isinstance(obj, cls):
            return obj
        if not isinstance(obj, dict):
            use_attributes = bool(from_attributes) or bool(
                getattr(cls, "model_config", {}).get("from_attributes", False)
            )
            if use_attributes:
                obj = {
                    name: getattr(obj, name)
                    for name in getattr(cls, "model_fields", {})
                    if hasattr(obj, name)
                }
            else:
                from ..errors import ErrorDetails, ValidationError

                raise ValidationError(
                    cls.__name__,
                    [ErrorDetails("model_type", (), "Input should be a valid mapping", obj)],
                )
        try:
            return cls(__tigrbl_strict__=bool(strict), __tigrbl_extra__=extra, **obj)
        except TypeError as exc:
            # Dataclass and simple-class Serde consumers do not accept engine options.
            if "__tigrbl_" not in str(exc):
                raise
            return cls(**obj)

    def to_dict(self, **options: Any) -> dict[str, Any]:
        return self.model_dump(**options)

    @classmethod
    def from_dict(cls, payload: dict[str, Any], **options: Any) -> Self:
        return cls.model_validate(payload, **options)


__all__ = ["SerdeMixin"]
