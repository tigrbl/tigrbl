"""YAML serialization and validation capability."""

from __future__ import annotations

from typing import Any
try:
    from typing import Self
except ImportError:  # pragma: no cover - Python 3.10 compatibility
    from typing_extensions import Self


class YamlMixin:
    def model_dump_yaml(self, **options: Any) -> str:
        import yaml

        payload = self.model_dump(mode="json", **options)  # type: ignore[attr-defined]
        return yaml.safe_dump(payload, sort_keys=False)

    @classmethod
    def model_validate_yaml(cls, yaml_data: str | bytes, **options: Any) -> Self:
        import yaml

        try:
            payload = yaml.safe_load(yaml_data)
        except yaml.YAMLError as exc:
            from ..errors import ErrorDetails, ValidationError

            raise ValidationError(
                cls.__name__,
                [ErrorDetails("yaml_invalid", (), f"Invalid YAML: {exc}", yaml_data)],
            ) from exc
        if not isinstance(payload, dict):
            from ..errors import ErrorDetails, ValidationError

            raise ValidationError(
                cls.__name__,
                [ErrorDetails("model_type", (), "YAML input should decode to a mapping", payload)],
            )
        return cls.model_validate(payload, **options)  # type: ignore[attr-defined]

    def to_yaml(self, **options: Any) -> str:
        return self.model_dump_yaml(**options)

    @classmethod
    def from_yaml(cls, payload: str | bytes, **options: Any) -> Self:
        return cls.model_validate_yaml(payload, **options)


__all__ = ["YamlMixin"]
