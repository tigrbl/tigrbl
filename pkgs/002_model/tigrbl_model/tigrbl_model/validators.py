"""Functional validator decorators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

ValidatorMode = Literal["before", "after", "plain", "wrap"]


@dataclass(frozen=True, slots=True)
class ValidatorSpec:
    kind: Literal["field", "model"]
    mode: ValidatorMode
    fields: tuple[str, ...] = ()


def _attach(target: Any, spec: ValidatorSpec) -> Any:
    raw = target.__func__ if isinstance(target, (classmethod, staticmethod)) else target
    specs = list(getattr(raw, "__tigrbl_validator_specs__", ()))
    specs.append(spec)
    setattr(raw, "__tigrbl_validator_specs__", tuple(specs))
    return target


def field_validator(
    *fields: str,
    mode: ValidatorMode = "after",
    **_: Any,
) -> Callable[[Any], Any]:
    if not fields:
        raise TypeError("field_validator requires at least one field name")

    def decorator(target: Any) -> Any:
        return _attach(target, ValidatorSpec("field", mode, tuple(fields)))

    return decorator


def model_validator(*, mode: ValidatorMode) -> Callable[[Any], Any]:
    def decorator(target: Any) -> Any:
        return _attach(target, ValidatorSpec("model", mode))

    return decorator


__all__ = ["field_validator", "model_validator"]
