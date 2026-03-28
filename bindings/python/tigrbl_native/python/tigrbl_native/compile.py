from __future__ import annotations

import json
from typing import Any

from .errors import NativeBindingsUnavailableError

try:
    from . import _native
except Exception as exc:  # pragma: no cover - exercised when extension is not built.
    _native = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def _require_native():
    if _native is None:
        raise NativeBindingsUnavailableError(
            "tigrbl_native._native is unavailable; build the maturin extension before compiling specs."
        ) from _IMPORT_ERROR
    return _native


def _coerce_spec(spec: Any) -> str:
    if isinstance(spec, str):
        return spec
    return json.dumps(spec, sort_keys=True)


def normalize_spec(spec: Any) -> str:
    native = _require_native()
    return native.normalize_spec(_coerce_spec(spec))


def compile_app(spec: Any) -> str:
    native = _require_native()
    return native.compile_spec(_coerce_spec(spec))
