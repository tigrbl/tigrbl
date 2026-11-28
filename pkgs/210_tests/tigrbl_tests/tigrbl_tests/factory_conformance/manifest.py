from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

_VALID_VERBS = {"activate", "define", "derive", "make", "provide"}
_VALID_FORMS = {
    "function",
    "classmethod",
    "staticmethod",
    "instance-method",
    "provider-callback",
    "compatibility",
}
_VALID_DESCRIPTORS = {"function", "classmethod", "staticmethod", "instance-method"}
_VALID_ASYNC = {"sync", "async"}


@dataclass(frozen=True, slots=True)
class FactoryAlias:
    path: str
    form: str
    stability: str = "stable"


@dataclass(frozen=True, slots=True)
class FactorySurface:
    path: str
    owner: str
    verb: str
    form: str
    descriptor: str
    async_mode: str
    returns: str
    side_effects: str
    stability: str
    family: str | None = None
    receiver: str | None = None
    canonical: str | None = None
    idempotency: str | None = None
    equivalence_group: str | None = None
    aliases: tuple[FactoryAlias, ...] = ()


@dataclass(frozen=True, slots=True)
class FactoryManifest:
    version: int
    surfaces: tuple[FactorySurface, ...]

    def by_path(self) -> dict[str, FactorySurface]:
        return {surface.path: surface for surface in self.surfaces}


def _parse_surface(value: dict[str, Any]) -> FactorySurface:
    aliases = tuple(FactoryAlias(**alias) for alias in value.pop("aliases", ()))
    surface = FactorySurface(aliases=aliases, **value)
    if surface.verb not in _VALID_VERBS:
        raise ValueError(f"unknown factory verb for {surface.path}: {surface.verb}")
    if surface.form not in _VALID_FORMS:
        raise ValueError(f"unknown factory form for {surface.path}: {surface.form}")
    if surface.descriptor not in _VALID_DESCRIPTORS:
        raise ValueError(
            f"unknown descriptor for {surface.path}: {surface.descriptor}"
        )
    if surface.async_mode not in _VALID_ASYNC:
        raise ValueError(f"unknown async mode for {surface.path}: {surface.async_mode}")
    return surface


def load_manifest(path: str | Path | None = None) -> FactoryManifest:
    if path is None:
        resource = files(__package__).joinpath("factory_surfaces.json")
        raw = json.loads(resource.read_text(encoding="utf-8"))
    else:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    surfaces = tuple(_parse_surface(dict(value)) for value in raw["surfaces"])
    canonical = [surface.path for surface in surfaces]
    aliases = [alias.path for surface in surfaces for alias in surface.aliases]
    if len(canonical) != len(set(canonical)):
        raise ValueError("factory manifest contains duplicate canonical paths")
    if set(canonical) & set(aliases) or len(aliases) != len(set(aliases)):
        raise ValueError("factory manifest contains duplicate or canonical aliases")
    return FactoryManifest(version=int(raw["version"]), surfaces=surfaces)
