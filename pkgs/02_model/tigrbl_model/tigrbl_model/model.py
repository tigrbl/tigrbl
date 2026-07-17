"""Tigrbl's Pydantic-independent model base and compiler."""

from __future__ import annotations

import copy
import inspect
import sys
import typing
from collections.abc import Mapping
from typing import Any, ClassVar, get_origin, get_type_hints

from .config import ConfigDict, merge_config
from .errors import ErrorDetails, ValidationError
from .fields import FieldInfo, PydanticUndefined
from .mixins import SerdeMixin
from .schema import model_json_schema as generate_json_schema
from .validation import ValidationIssue, validate_value


def _validator_specs(namespace: dict[str, Any]) -> list[tuple[str, Any]]:
    results = []
    for name, descriptor in namespace.items():
        raw = descriptor.__func__ if isinstance(descriptor, (classmethod, staticmethod)) else descriptor
        for spec in getattr(raw, "__tigrbl_validator_specs__", ()):
            results.append((name, spec))
    return results


def _invoke_before(function: Any, cls: type, value: Any) -> Any:
    parameters = inspect.signature(function).parameters
    return function(cls, value) if len(parameters) >= 2 else function(value)


class ModelMeta(type):
    """Collect annotated fields and functional validators at class creation."""

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> "ModelMeta":
        fields: dict[str, FieldInfo] = {}
        configs: list[dict[str, Any]] = []
        validators: list[tuple[str, Any]] = []
        for base in bases:
            fields.update(copy.deepcopy(getattr(base, "model_fields", {})))
            configs.append(getattr(base, "model_config", {}))
            validators.extend(getattr(base, "__tigrbl_validators__", ()))

        own_config = namespace.get("model_config")
        annotations = dict(namespace.get("__annotations__", {}))
        raw_annotations: dict[str, Any] = {}
        for field_name, annotation in annotations.items():
            if field_name.startswith("_") or get_origin(annotation) is ClassVar:
                continue
            if isinstance(annotation, str) and "ClassVar" in annotation:
                continue
            raw_annotations[field_name] = annotation
            declared = namespace.get(field_name, PydanticUndefined)
            if isinstance(declared, FieldInfo):
                info = copy.deepcopy(declared)
                info.annotation = annotation
            else:
                info = FieldInfo(annotation=annotation, default=declared)
            fields[field_name] = info

        namespace["model_fields"] = fields
        namespace["model_config"] = merge_config(*configs, own_config)
        namespace["__tigrbl_raw_annotations__"] = raw_annotations
        validators.extend(_validator_specs(namespace))
        namespace["__tigrbl_validators__"] = tuple(validators)
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls


class Model(SerdeMixin, metaclass=ModelMeta):
    """Validated model with Pydantic-shaped methods required by Tigrbl."""

    model_config: ClassVar[ConfigDict] = ConfigDict()
    model_fields: ClassVar[dict[str, FieldInfo]] = {}
    __root_model__: ClassVar[bool] = False

    def __init__(self, **data: Any) -> None:
        strict = bool(data.pop("__tigrbl_strict__", False))
        extra_override = data.pop("__tigrbl_extra__", None)
        cls = type(self)
        cls.model_rebuild(raise_errors=False)

        for name, spec in cls.__tigrbl_validators__:
            if spec.kind == "model" and spec.mode == "before":
                function = getattr(cls, name)
                try:
                    data = _invoke_before(function, cls, data)
                except (TypeError, ValueError, AssertionError) as exc:
                    raise ValidationError(
                        cls.__name__,
                        [ErrorDetails("value_error", (), f"Value error, {exc}", data)],
                    ) from exc
                if not isinstance(data, Mapping):
                    raise ValidationError(
                        cls.__name__,
                        [ErrorDetails("model_type", (), "Model before validator should return a mapping", data)],
                    )
                data = dict(data)

        errors: list[ErrorDetails] = []
        values: dict[str, Any] = {}
        fields_set: set[str] = set()
        consumed: set[str] = set()
        populate_by_name = bool(cls.model_config.get("populate_by_name"))

        for field_name, field in cls.model_fields.items():
            candidates = list(field.validation_names(field_name))
            if populate_by_name and field_name not in candidates:
                candidates.append(field_name)
            source_name = next((candidate for candidate in candidates if candidate in data), None)
            location_name = source_name or candidates[0]
            if source_name is None:
                if field.is_required():
                    errors.append(
                        ErrorDetails("missing", (location_name,), "Field required", data)
                    )
                    continue
                value = field.get_default(call_default_factory=True)
                if not cls.model_config.get("validate_default"):
                    values[field_name] = value
                    continue
            else:
                value = data[source_name]
                consumed.add(source_name)
                fields_set.add(field_name)

            try:
                for validator_name, spec in cls.__tigrbl_validators__:
                    if spec.kind == "field" and field_name in spec.fields and spec.mode == "before":
                        function = getattr(cls, validator_name)
                        value = _invoke_before(function, cls, value)
                value = validate_value(
                    field.annotation,
                    value,
                    field=field,
                    loc=(location_name,),
                    strict=strict,
                    arbitrary_types_allowed=bool(cls.model_config.get("arbitrary_types_allowed")),
                )
                for validator_name, spec in cls.__tigrbl_validators__:
                    if spec.kind == "field" and field_name in spec.fields and spec.mode == "after":
                        function = getattr(cls, validator_name)
                        value = _invoke_before(function, cls, value)
                values[field_name] = value
            except ValidationIssue as exc:
                errors.append(exc.details)
            except ValidationError as exc:
                for item in exc.errors(include_url=False):
                    errors.append(
                        ErrorDetails(
                            item["type"],
                            (location_name, *tuple(item["loc"])),
                            item["msg"],
                            item.get("input"),
                            item.get("ctx"),
                        )
                    )
            except (TypeError, ValueError, AssertionError) as exc:
                errors.append(
                    ErrorDetails("value_error", (location_name,), f"Value error, {exc}", value)
                )

        extra_values = {key: value for key, value in data.items() if key not in consumed}
        extra_policy = extra_override or cls.model_config.get("extra", "ignore")
        if extra_policy == "forbid":
            errors.extend(
                ErrorDetails("extra_forbidden", (key,), "Extra inputs are not permitted", value)
                for key, value in extra_values.items()
            )
        if errors:
            raise ValidationError(cls.__name__, errors)

        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "__model_fields_set__", fields_set)
        object.__setattr__(
            self, "__model_extra__", extra_values if extra_policy == "allow" else {}
        )
        if extra_policy == "allow":
            for name, value in extra_values.items():
                object.__setattr__(self, name, value)

        for name, spec in cls.__tigrbl_validators__:
            if spec.kind == "model" and spec.mode == "after":
                function = getattr(self, name)
                try:
                    result = function()
                except (TypeError, ValueError, AssertionError) as exc:
                    raise ValidationError(
                        cls.__name__,
                        [
                            ErrorDetails(
                                "value_error",
                                (),
                                f"Value error, {exc}",
                                self.model_dump(),
                            )
                        ],
                    ) from exc
                if result is not None and result is not self:
                    for field_name in cls.model_fields:
                        if hasattr(result, field_name):
                            object.__setattr__(self, field_name, getattr(result, field_name))

    @property
    def model_fields_set(self) -> set[str]:
        return set(self.__model_fields_set__)

    @property
    def model_extra(self) -> dict[str, Any] | None:
        return dict(self.__model_extra__) if self.__model_extra__ else None

    @property
    def model_computed_fields(self) -> dict[str, Any]:
        return {}

    @classmethod
    def model_construct(cls, _fields_set: set[str] | None = None, **values: Any) -> "Model":
        instance = cls.__new__(cls)
        supplied = {name for name in values if name in cls.model_fields}
        resolved: dict[str, Any] = {}
        for name, field in cls.model_fields.items():
            if name in values:
                resolved[name] = values.pop(name)
            elif not field.is_required():
                resolved[name] = field.get_default(call_default_factory=True)
        for name, value in resolved.items():
            object.__setattr__(instance, name, value)
        extra_policy = cls.model_config.get("extra")
        object.__setattr__(instance, "__model_extra__", dict(values) if extra_policy == "allow" else {})
        if extra_policy == "allow":
            for name, value in values.items():
                object.__setattr__(instance, name, value)
        object.__setattr__(
            instance,
            "__model_fields_set__",
            set(_fields_set) if _fields_set is not None else supplied,
        )
        return instance

    @classmethod
    def model_rebuild(
        cls,
        *,
        force: bool = False,
        raise_errors: bool = True,
        _types_namespace: dict[str, Any] | None = None,
        **_: Any,
    ) -> bool | None:
        if not force and all(not isinstance(item.annotation, str) for item in cls.model_fields.values()):
            return None
        namespace = dict(vars(typing))
        namespace.update(vars(sys.modules[Model.__module__]))
        namespace.update(vars(sys.modules[cls.__module__]))
        namespace.update(_types_namespace or {})
        namespace.setdefault(cls.__name__, cls)
        try:
            hints = get_type_hints(cls, globalns=namespace, localns=namespace, include_extras=True)
        except (NameError, TypeError):
            if raise_errors:
                raise
            return False
        for name, annotation in hints.items():
            if name in cls.model_fields:
                cls.model_fields[name].annotation = annotation
        return True

    @classmethod
    def model_json_schema(
        cls,
        *,
        by_alias: bool = True,
        ref_template: str = "#/$defs/{model}",
        schema_generator: Any = None,
        mode: str = "validation",
    ) -> dict[str, Any]:
        del schema_generator
        cls.model_rebuild(raise_errors=False)
        return generate_json_schema(cls, by_alias=by_alias, ref_template=ref_template, mode=mode)

    def model_copy(
        self,
        *,
        update: Mapping[str, Any] | None = None,
        deep: bool = False,
    ) -> "Model":
        values = self.model_dump(mode="python")
        values.update(update or {})
        return type(self).model_construct(
            _fields_set=self.model_fields_set | set(update or {}),
            **(copy.deepcopy(values) if deep else values),
        )

    def __iter__(self):
        yield from self.model_dump().items()

    def __repr__(self) -> str:
        parts = []
        for name, field in type(self).model_fields.items():
            if field.repr and hasattr(self, name):
                parts.append(f"{name}={getattr(self, name)!r}")
        return f"{type(self).__name__}({', '.join(parts)})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self.model_dump() == other.model_dump()


BaseModel = Model


__all__ = ["BaseModel", "Model", "ModelMeta"]
