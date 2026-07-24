from __future__ import annotations

import inspect

from .manifest import FactorySurface
from .resolution import resolve_symbol


def assert_surface_shape(surface: FactorySurface) -> None:
    value = resolve_symbol(surface.path)
    expected_async = surface.async_mode == "async"
    assert inspect.iscoroutinefunction(value) is expected_async, (
        f"async mode mismatch for {surface.path}"
    )
    if surface.verb == "provide":
        assert surface.side_effects in {"none", "dependency-access"}, (
            f"provide surface {surface.path} must expose/acquire a dependency"
        )
    if surface.verb == "define":
        assert surface.side_effects == "none", (
            f"define surface {surface.path} must be declarative"
        )
