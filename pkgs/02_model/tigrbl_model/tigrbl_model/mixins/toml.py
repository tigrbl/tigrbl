"""TOML serialization and validation capability."""

from __future__ import annotations

from typing import Any
try:
    from typing import Self
except ImportError:  # pragma: no cover - Python 3.10 compatibility
    from typing_extensions import Self

from ..serialization import strip_toml_nulls


class TomlMixin:
    def model_dump_toml(self, **options: Any) -> str:
        import tomli_w

        payload = self.model_dump(mode="json", **options)  # type: ignore[attr-defined]
        return tomli_w.dumps(strip_toml_nulls(payload))

    @classmethod
    def model_validate_toml(cls, toml_data: str | bytes, **options: Any) -> Self:
        try:
            import tomllib
        except ModuleNotFoundError:  # pragma: no cover - Python 3.10
            import tomli as tomllib  # type: ignore[no-redef]

        text = toml_data.decode("utf-8") if isinstance(toml_data, bytes) else toml_data
        try:
            payload = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            from ..errors import ErrorDetails, ValidationError

            raise ValidationError(
                cls.__name__,
                [ErrorDetails("toml_invalid", (), f"Invalid TOML: {exc}", text)],
            ) from exc
        return cls.model_validate(payload, **options)  # type: ignore[attr-defined]

    def to_toml(self, **options: Any) -> str:
        return self.model_dump_toml(**options)

    @classmethod
    def from_toml(cls, payload: str | bytes, **options: Any) -> Self:
        return cls.model_validate_toml(payload, **options)


__all__ = ["TomlMixin"]
