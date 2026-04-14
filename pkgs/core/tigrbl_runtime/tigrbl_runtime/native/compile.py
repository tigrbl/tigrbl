from __future__ import annotations

import json
from typing import Any

from .codec import coerce_native_spec_json
from .errors import NativeBindingsUnavailableError
from ._load_native import load_native_module

_native, _IMPORT_ERROR = load_native_module()


def _require_native():
    if _native is None:
        raise NativeBindingsUnavailableError(
            "tigrbl_runtime.native._native is unavailable; build the runtime extension before compiling native specs."
        ) from _IMPORT_ERROR
    return _native


def _coerce_spec(spec: Any) -> str:
    return coerce_native_spec_json(spec)


def normalize_spec(spec: Any) -> str:
    native = _require_native()
    return native.normalize_spec(_coerce_spec(spec))


def compile_app(spec: Any) -> dict[str, Any]:
    native = _require_native()
    compiled = native.compile_spec(_coerce_spec(spec))
    if isinstance(compiled, str):
        return json.loads(compiled)
    return compiled
