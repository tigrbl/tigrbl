from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple

from .serde import SerdeMixin


def _normalize_header_name(name: object) -> str:
    if isinstance(name, (bytes, bytearray)):
        return name.decode("latin-1").lower()
    return str(name).lower()


def _normalize_header_value(value: object) -> str:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("latin-1")
    return str(value)


@dataclass(frozen=True, slots=True)
class HeadersSpec(SerdeMixin):
    """Declarative HTTP header collection contract.

    Headers are modeled as a plural collection because request and response
    surfaces operate on mappings of header names to serialized values. Runtime
    implementations may preserve richer lookup behavior, but the spec shape
    remains a portable string collection.
    """

    values: Dict[str, str] = field(default_factory=dict)
    required: Tuple[str, ...] = ()
    expose: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            {
                _normalize_header_name(key): _normalize_header_value(value)
                for key, value in self.values.items()
            },
        )
        object.__setattr__(
            self,
            "required",
            tuple(_normalize_header_name(name) for name in self.required),
        )
        object.__setattr__(
            self,
            "expose",
            tuple(_normalize_header_name(name) for name in self.expose),
        )

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, str],
        *,
        required: Tuple[str, ...] = (),
        expose: Tuple[str, ...] = (),
    ) -> "HeadersSpec":
        return cls(values=dict(values), required=required, expose=expose)

    def as_dict(self) -> dict[str, str]:
        return dict(self.values)

    def items(self):
        return self.values.items()

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(_normalize_header_name(key), default)


__all__ = ["HeadersSpec"]
