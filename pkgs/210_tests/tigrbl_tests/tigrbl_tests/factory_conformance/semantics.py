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
    if surface.verb == "derive":
        assert surface.side_effects == "none", (
            f"derive surface {surface.path} must be deterministic"
        )
    if surface.verb == "make":
        assert surface.side_effects == "construction", (
            f"make surface {surface.path} must construct its declared product"
        )
    if surface.verb == "activate":
        assert surface.side_effects in {
            "binding",
            "initialization",
            "registration",
            "runtime-mutation",
        }, f"activate surface {surface.path} must declare runtime effects"
    if surface.form == "classmethod":
        assert surface.canonical, (
            f"classmethod surface {surface.path} must declare a canonical function"
        )
