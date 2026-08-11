from __future__ import annotations

from .manifest import FactorySurface

_OWNER_PREFIXES = {
    "base": ("tigrbl_base.",),
    "concrete": ("tigrbl_concrete.",),
    "core": ("tigrbl_core.",),
    "experimental": ("tigrbl_mcp:",),
    "kernel": ("tigrbl_kernel.",),
}


def assert_owner(surface: FactorySurface) -> None:
    if surface.owner == "core" and surface.verb == "make":
        raise AssertionError("core must not own public construction factories")
    prefixes = _OWNER_PREFIXES.get(surface.owner)
    if prefixes is None:
        raise AssertionError(f"unknown factory owner: {surface.owner}")
    assert surface.path.startswith(prefixes), (
        f"{surface.path} is declared in owner {surface.owner} but has wrong prefix"
    )
