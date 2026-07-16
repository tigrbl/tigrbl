"""Engine plugin discovery helpers.

Plugins are loaded via the ``tigrbl.engine_plugins`` entry point group.
Each entry point may resolve to either:
- a callable that performs registration side effects, or
- a module/object exposing a ``register()`` callable.
"""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any

_LOADED = False


def _invoke_plugin(obj: Any) -> None:
    if callable(obj):
        obj()
        return
    register = getattr(obj, "register", None)
    if callable(register):
        register()


def load_engine_plugins() -> None:
    """Load engine plugins once per process."""
    global _LOADED
    if _LOADED:
        return

    discovered = []
    for group in ("tigrbl.engine_plugins", "tigrbl.engine"):
        try:
            discovered.extend(entry_points(group=group))
        except TypeError:  # pragma: no cover
            discovered.extend(entry_points().get(group, []))

    loaded_names: set[str] = set()
    for ep in discovered:
        name = str(getattr(ep, "name", ""))
        if name in loaded_names:
            continue
        try:
            _invoke_plugin(ep.load())
            loaded_names.add(name)
        except Exception:
            # EngineSpec handles missing registrations with explicit error text.
            continue

    _LOADED = True
