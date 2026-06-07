from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .serde import SerdeMixin

WELL_KNOWN_PREFIX = "/.well-known"


@dataclass(frozen=True)
class WellKnownResourceSpec(SerdeMixin):
    """Declarative AppSpec resource served under ``/.well-known/{name}``."""

    name: str
    payload: Any
    media_type: str = "application/json"
    status_code: int = 200
    headers: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        normalize_well_known_name(self.name)
        if not isinstance(self.media_type, str) or not self.media_type.strip():
            raise ValueError("WellKnownResourceSpec.media_type must be a string.")
        if int(self.status_code) < 100 or int(self.status_code) > 599:
            raise ValueError("WellKnownResourceSpec.status_code must be an HTTP status.")
        if self.headers is not None and not isinstance(self.headers, Mapping):
            raise TypeError("WellKnownResourceSpec.headers must be a mapping.")


def normalize_well_known_name(name: str) -> str:
    token = str(name or "").strip()
    if token.startswith(f"{WELL_KNOWN_PREFIX}/"):
        token = token[len(WELL_KNOWN_PREFIX) + 1 :]
    elif token.startswith("/"):
        raise ValueError(
            "Well-known resource names must be relative or start with "
            f"{WELL_KNOWN_PREFIX}/."
        )
    token = token.strip("/")
    if not token:
        raise ValueError("Well-known resource name must not be empty.")
    parts = token.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Invalid well-known resource name: {name!r}.")
    if any("?" in part or "#" in part for part in parts):
        raise ValueError(f"Invalid well-known resource name: {name!r}.")
    return "/".join(parts)


def well_known_path(name: str) -> str:
    return f"{WELL_KNOWN_PREFIX}/{normalize_well_known_name(name)}"


__all__ = [
    "WELL_KNOWN_PREFIX",
    "WellKnownResourceSpec",
    "normalize_well_known_name",
    "well_known_path",
]
