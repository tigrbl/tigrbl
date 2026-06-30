"""Runtime public API with lazy imports to avoid circular startup."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "build_asgi_channel": "channel",
    "prepare_channel_context": "channel",
    "RuntimeBase": "base",
    "Runtime": "runtime",
    "GwRawEnvelope": "_typing_aliases",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
