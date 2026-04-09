from __future__ import annotations

from typing import Any

from ._parity_contract import build_parity_snapshot as _reference_snapshot
from ._parity_contract import transport_trace as _reference_trace
from .errors import NativeBindingsUnavailableError

try:
    from . import _native
except Exception as exc:  # pragma: no cover
    _native = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def _require_native():
    if _native is None:
        raise NativeBindingsUnavailableError(
            "tigrbl_native._native is unavailable; build the extension or use the source fallback."
        ) from _IMPORT_ERROR
    return _native


def reference_parity_snapshot(spec: Any) -> dict[str, object]:
    return _reference_snapshot(spec)


def native_parity_snapshot(spec: Any) -> dict[str, object]:
    native = _require_native()
    if hasattr(native, "build_parity_snapshot"):
        return dict(native.build_parity_snapshot(spec))
    return _reference_snapshot(spec)


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


def native_transport_trace(
    transport: str,
    *,
    include_hook: bool = False,
    include_error: bool = False,
    include_docs: bool = False,
) -> list[dict[str, object]]:
    native = _require_native()
    if hasattr(native, "transport_trace"):
        return list(
            native.transport_trace(
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
