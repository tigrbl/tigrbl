from __future__ import annotations

from types import ModuleType

from .errors import RUST_DEPRECATION_MESSAGE


_LOADED: ModuleType | None = None
_IMPORT_ERROR: Exception | None = None


def load_rust_module() -> tuple[ModuleType, Exception | None]:
    global _LOADED, _IMPORT_ERROR

    if _LOADED is not None:
        return _LOADED, _IMPORT_ERROR

    from . import _fallback as module

    _LOADED = module
    _IMPORT_ERROR = RuntimeError(RUST_DEPRECATION_MESSAGE)
    return _LOADED, _IMPORT_ERROR
