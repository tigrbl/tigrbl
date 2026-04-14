from __future__ import annotations

from typing import Any

from ._parity_contract import build_parity_snapshot as _reference_snapshot
from ._parity_contract import transport_trace as _reference_trace
from .codec import coerce_rust_spec_dict
from .errors import RustBindingsUnavailableError
from ._load_rust import load_rust_module

_rust, _IMPORT_ERROR = load_rust_module()


def _require_rust():
    if _rust is None:
        raise RustBindingsUnavailableError(
            "tigrbl_runtime.rust._rust is unavailable; build the runtime extension or use the source fallback."
        ) from _IMPORT_ERROR
    return _rust


def reference_parity_snapshot(spec: Any) -> dict[str, object]:
    return _reference_snapshot(coerce_rust_spec_dict(spec))


def rust_parity_snapshot(spec: Any) -> dict[str, object]:
    rust = _require_rust()
    payload = coerce_rust_spec_dict(spec)
    if hasattr(rust, "build_parity_snapshot"):
        return dict(rust.build_parity_snapshot(payload))
    return _reference_snapshot(payload)


def reference_transport_trace(
    transport: str,
    *,
    include_hook: bool = False,
    include_error: bool = False,
    include_docs: bool = False,
) -> list[dict[str, object]]:
    return _reference_trace(
        transport,
        include_hook=include_hook,
        include_error=include_error,
        include_docs=include_docs,
    )


def rust_transport_trace(
    transport: str,
    *,
    include_hook: bool = False,
    include_error: bool = False,
    include_docs: bool = False,
) -> list[dict[str, object]]:
    rust = _require_rust()
    if hasattr(rust, "transport_trace"):
        return list(
            rust.transport_trace(
                transport,
                include_hook=include_hook,
                include_error=include_error,
                include_docs=include_docs,
            )
        )
    return _reference_trace(
        transport,
        include_hook=include_hook,
        include_error=include_error,
        include_docs=include_docs,
    )
