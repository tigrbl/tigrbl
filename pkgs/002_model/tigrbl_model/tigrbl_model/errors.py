"""Structured model validation errors."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class ErrorDetails:
    """One validation failure with a stable location and machine-readable type."""

    type: str
    loc: tuple[str | int, ...]
    msg: str
    input: Any = None
    ctx: dict[str, Any] | None = None

    def as_dict(self, *, include_url: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "loc": self.loc,
            "msg": self.msg,
            "input": self.input,
        }
        if self.ctx:
            result["ctx"] = dict(self.ctx)
        if include_url:
            result["url"] = f"https://errors.tigrbl.dev/model/{self.type}"
        return result


class ValidationError(ValueError):
    """Aggregate validation failures for a model operation."""

    def __init__(self, title: str, errors: Iterable[ErrorDetails | dict[str, Any]]):
        self.title = title
        self._errors = tuple(
            error
            if isinstance(error, ErrorDetails)
            else ErrorDetails(
                type=str(error.get("type", "value_error")),
                loc=tuple(error.get("loc", ())),
                msg=str(error.get("msg", "Invalid value")),
                input=error.get("input"),
                ctx=error.get("ctx"),
            )
            for error in errors
        )
        super().__init__(str(self))

    @classmethod
    def from_exception_data(
        cls, title: str, line_errors: Iterable[dict[str, Any]]
    ) -> "ValidationError":
        return cls(title, line_errors)

    def error_count(self) -> int:
        return len(self._errors)

    def errors(
        self,
        *,
        include_url: bool = True,
        include_context: bool = True,
        include_input: bool = True,
    ) -> list[dict[str, Any]]:
        values = [error.as_dict(include_url=include_url) for error in self._errors]
        for value in values:
            if not include_context:
                value.pop("ctx", None)
            if not include_input:
                value.pop("input", None)
        return values

    def json(self, *, indent: int | None = None, **_: Any) -> str:
        return json.dumps(self.errors(), indent=indent, default=str)

    def __str__(self) -> str:
        count = len(self._errors)
        heading = f"{count} validation error{'s' if count != 1 else ''} for {self.title}"
        lines = [heading]
        for error in self._errors:
            location = ".".join(str(item) for item in error.loc) or "__root__"
            lines.extend((location, f"  {error.msg} [type={error.type}]"))
        return "\n".join(lines)


class ModelUserError(TypeError):
    """Raised when a declaration uses a removed or unsupported model option."""

    def __init__(self, message: str, *, code: str = "model-user-error") -> None:
        self.code = code
        super().__init__(message)


__all__ = ["ErrorDetails", "ModelUserError", "ValidationError"]
