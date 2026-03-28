from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .compile import _coerce_spec
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
            "tigrbl_native._native is unavailable; build the maturin extension before instantiating the native runtime."
        ) from _IMPORT_ERROR
    return _native


@dataclass(slots=True)
class NativeRuntimeHandle:
    _handle: Any

    def describe(self) -> str:
        return self._handle.describe()

    def begin_request(self, transport: str = "rest") -> None:
        if hasattr(self._handle, "begin_request"):
            self._handle.begin_request(transport)

    def callback_fence(self, kind: str, name: str) -> None:
        if hasattr(self._handle, "callback_fence"):
            self._handle.callback_fence(kind, name)

    def finish_response(self, transport: str = "rest") -> None:
        if hasattr(self._handle, "finish_response"):
            self._handle.finish_response(transport)

    def ffi_events(self) -> list[dict[str, object]]:
        if hasattr(self._handle, "ffi_events"):
            return list(self._handle.ffi_events())
        return []


def create_runtime(spec: Any) -> NativeRuntimeHandle:
    native = _require_native()
    handle = native.create_runtime_handle(_coerce_spec(spec))
    return NativeRuntimeHandle(handle)
