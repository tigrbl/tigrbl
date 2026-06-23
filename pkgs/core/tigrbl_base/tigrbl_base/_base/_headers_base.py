from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from tigrbl_core._spec.headers_spec import HeadersSpec


HeaderInput = Iterable[tuple[str, str]] | Mapping[str, str] | HeadersSpec | None


def _normalize_header_name(name: Any) -> str:
    if isinstance(name, (bytes, bytearray)):
        return name.decode("latin-1").lower()
    return str(name).lower()


def _normalize_header_value(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("latin-1")
    return str(value)


def _iter_header_items(values: HeaderInput):
    if values is None:
        return ()
    if isinstance(values, HeadersSpec):
        return values.values.items()
    if hasattr(values, "items"):
        return values.items()  # type: ignore[union-attr]
    return values


class HeadersBase(dict[str, str]):
    """Base header mapping type for response implementations."""

    required: tuple[str, ...]
    expose: tuple[str, ...]

    def __init__(
        self,
        values: HeaderInput = None,
        *,
        required: tuple[str, ...] = (),
        expose: tuple[str, ...] = (),
    ) -> None:
        if isinstance(values, HeadersSpec):
            required = values.required
            expose = values.expose
        super().__init__(
            {
                _normalize_header_name(key): _normalize_header_value(value)
                for key, value in _iter_header_items(values)
            }
        )
        self.required = tuple(_normalize_header_name(name) for name in required)
        self.expose = tuple(_normalize_header_name(name) for name in expose)

    def __getitem__(self, key: str) -> str:
        return super().__getitem__(_normalize_header_name(key))

    def __contains__(self, key: object) -> bool:
        if isinstance(key, (str, bytes, bytearray)):
            return super().__contains__(_normalize_header_name(key))
        return super().__contains__(key)

    def get(self, key: str, default: Any = None) -> str | Any:
        return super().get(_normalize_header_name(key), default)

    @property
    def raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [
            (key.encode("latin-1"), value.encode("latin-1"))
            for key, value in self.items()
        ]

    def as_spec(self) -> HeadersSpec:
        return HeadersSpec(values=dict(self), required=self.required, expose=self.expose)


class HeaderCookiesBase(dict[str, str]):
    """Base cookie mapping type for response implementations."""


__all__ = ["HeaderCookiesBase", "HeadersBase"]
