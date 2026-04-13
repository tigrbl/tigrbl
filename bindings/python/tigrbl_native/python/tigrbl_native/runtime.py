from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .compile import _coerce_spec
from .errors import NativeBindingsUnavailableError

try:
    from . import _native
except Exception as exc:  # pragma: no cover - exercised when extension is not built.
    from . import _fallback as _native
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

    def plan(self) -> dict[str, object]:
        if hasattr(self._handle, "plan_json"):
            return json.loads(self._handle.plan_json())
        return {}

    def execute_rest(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_spec(envelope)
        if hasattr(self._handle, "execute_rest_json"):
            return json.loads(self._handle.execute_rest_json(payload))
        raise NativeBindingsUnavailableError("native runtime handle cannot execute REST envelopes")

    def execute_jsonrpc(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_spec(envelope)
        if hasattr(self._handle, "execute_jsonrpc_json"):
            return json.loads(self._handle.execute_jsonrpc_json(payload))
        raise NativeBindingsUnavailableError(
            "native runtime handle cannot execute JSON-RPC envelopes"
        )

    def execute_ws(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_spec(envelope)
        if hasattr(self._handle, "execute_ws_json"):
            return json.loads(self._handle.execute_ws_json(payload))
        raise NativeBindingsUnavailableError("native runtime handle cannot execute websocket envelopes")

    def execute_stream(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_spec(envelope)
        if hasattr(self._handle, "execute_stream_json"):
            return json.loads(self._handle.execute_stream_json(payload))
        raise NativeBindingsUnavailableError("native runtime handle cannot execute streaming envelopes")

    def execute_sse(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_spec(envelope)
        if hasattr(self._handle, "execute_sse_json"):
            return json.loads(self._handle.execute_sse_json(payload))
        raise NativeBindingsUnavailableError("native runtime handle cannot execute SSE envelopes")

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
            events = self._handle.ffi_events()
            if isinstance(events, str):
                return list(json.loads(events))
            return list(events)
        return []


def create_runtime(spec: Any) -> NativeRuntimeHandle:
    native = _require_native()
    from .compile import compile_app

    compiled = compile_app(spec)
    handle = native.create_runtime_handle(_coerce_spec(compiled))
    return NativeRuntimeHandle(handle)
