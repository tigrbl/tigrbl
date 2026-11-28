"""JSON serialization and validation capability."""

from __future__ import annotations

import json
from typing import Any
try:
    from typing import Self
except ImportError:  # pragma: no cover - Python 3.10 compatibility
    from typing_extensions import Self


class JsonMixin:
    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        fallback: Any = None,
        **_: Any,
    ) -> str:
        payload = self.model_dump(  # type: ignore[attr-defined]
            mode="json",
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            fallback=fallback,
        )
        separators = None if indent is not None else (",", ":")
        return json.dumps(payload, indent=indent, separators=separators, ensure_ascii=False)

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        try:
            payload = json.loads(json_data)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            from ..errors import ErrorDetails, ValidationError

            raise ValidationError(
                cls.__name__,
                [ErrorDetails("json_invalid", (), f"Invalid JSON: {exc}", json_data)],
            ) from exc
        return cls.model_validate(  # type: ignore[attr-defined]
            payload,
            strict=bool(strict),
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )

    def to_json(self, *, indent: int | None = None, **options: Any) -> str:
        return self.model_dump_json(indent=indent, **options)

    @classmethod
    def from_json(cls, payload: str | bytes | bytearray, **options: Any) -> Self:
        return cls.model_validate_json(payload, **options)


__all__ = ["JsonMixin"]
