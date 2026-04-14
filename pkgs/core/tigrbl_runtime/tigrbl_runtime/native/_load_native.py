from __future__ import annotations

from types import ModuleType


_LOADED: ModuleType | None = None
_IMPORT_ERROR: Exception | None = None


def load_native_module() -> tuple[ModuleType, Exception | None]:
    global _LOADED, _IMPORT_ERROR

    if _LOADED is not None:
        return _LOADED, _IMPORT_ERROR

    try:
        from . import _native as module
    except Exception as exc:
        _IMPORT_ERROR = exc
    else:
        _LOADED = module
        _IMPORT_ERROR = None
        return _LOADED, _IMPORT_ERROR

    from . import _fallback as module

    _LOADED = module
    return _LOADED, _IMPORT_ERROR
