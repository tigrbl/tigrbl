from __future__ import annotations

import json
from typing import Any

from .codec import coerce_rust_spec_json
from .errors import RustBindingsUnavailableError
from ._load_rust import load_rust_module

_rust, _IMPORT_ERROR = load_rust_module()


def _require_rust():
    if _rust is None:
        raise RustBindingsUnavailableError(
            "tigrbl_runtime.rust._rust is unavailable; build the runtime extension before compiling rust specs."
        ) from _IMPORT_ERROR
    return _rust


def _coerce_spec(spec: Any) -> str:
    return coerce_rust_spec_json(spec)


def normalize_spec(spec: Any) -> str:
    rust = _require_rust()
    return rust.normalize_spec(_coerce_spec(spec))


def compile_app(spec: Any) -> dict[str, Any]:
    rust = _require_rust()
    compiled = rust.compile_spec(_coerce_spec(spec))
    if isinstance(compiled, str):
        return json.loads(compiled)
    return compiled
