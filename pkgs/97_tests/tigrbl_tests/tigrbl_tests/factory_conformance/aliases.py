from __future__ import annotations

import inspect

from .manifest import FactoryAlias, FactorySurface
from .resolution import resolve_symbol


def assert_alias_parity(surface: FactorySurface, alias: FactoryAlias) -> None:
    canonical = resolve_symbol(surface.path)
    candidate = resolve_symbol(alias.path)
    if alias.form in {"identity", "re-export"}:
        assert candidate is canonical, (
            f"{alias.path} must preserve identity with {surface.path}"
        )
    assert inspect.signature(candidate) == inspect.signature(canonical), (
        f"signature drift: {alias.path} != {surface.path}"
    )
    assert inspect.iscoroutinefunction(candidate) == inspect.iscoroutinefunction(canonical), (
        f"async drift: {alias.path} != {surface.path}"
    )
