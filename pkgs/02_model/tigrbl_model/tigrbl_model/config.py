"""Model configuration primitives."""

from __future__ import annotations

from typing import Any


class ConfigDict(dict[str, Any]):
    """Dictionary configuration compatible with Tigrbl's Pydantic usage."""


ModelConfig = ConfigDict


DEFAULT_CONFIG = ConfigDict(
    extra="ignore",
    populate_by_name=False,
    from_attributes=False,
    arbitrary_types_allowed=False,
    validate_default=False,
    use_enum_values=False,
    json_schema_extra=None,
)


def merge_config(*configs: dict[str, Any] | None) -> ConfigDict:
    """Merge model configuration from oldest base to newest declaration."""

    merged = ConfigDict(DEFAULT_CONFIG)
    for config in configs:
        if config:
            merged.update(config)
    return merged


__all__ = ["ConfigDict", "ModelConfig"]
