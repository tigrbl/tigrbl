from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import Any

from tigrbl_core.config.constants import TIGRBL_DEFAULT_ROOT_ALIAS

from .errors import RustBindingsUnavailableError
from ._load_rust import load_rust_module

_rust, _IMPORT_ERROR = load_rust_module()


def _require_rust():
    if _rust is None:
        raise RustBindingsUnavailableError(
            "tigrbl_runtime.rust._rust is unavailable; build the runtime extension before instantiating the rust runtime."
        ) from _IMPORT_ERROR
    return _rust


def _coerce_compiled_plan(plan: Any) -> str:
    if isinstance(plan, str):
        payload = json.loads(plan)
        if not isinstance(payload, dict):
            raise TypeError("rust runtime expects a compiled plan JSON object")
        return json.dumps(payload, sort_keys=True)
    if isinstance(plan, Mapping):
        return json.dumps(dict(plan), sort_keys=True)
    raise TypeError(
        "create_runtime_from_compiled expects a compiled plan mapping or JSON object"
    )


def _coerce_request_payload(envelope: Any) -> str:
    if isinstance(envelope, str):
        payload = json.loads(envelope)
        if not isinstance(payload, dict):
            raise TypeError("rust runtime expects a request JSON object")
        return json.dumps(payload, sort_keys=True)
    if isinstance(envelope, Mapping):
        return json.dumps(dict(envelope), sort_keys=True)
    asdict = getattr(envelope, "asdict", None)
    if callable(asdict):
        payload = asdict()
        if isinstance(payload, Mapping):
            return json.dumps(dict(payload), sort_keys=True)
    raise TypeError("rust runtime expects a request mapping or JSON object")

@dataclass(slots=True)
class RustRuntimeHandle:
    _handle: Any

    def describe(self) -> str:
        return self._handle.describe()

    def plan(self) -> dict[str, object]:
        if hasattr(self._handle, "plan_json"):
            return json.loads(self._handle.plan_json())
        return {}

    def execute_rest(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_request_payload(envelope)
        if hasattr(self._handle, "execute_rest_json"):
            return json.loads(self._handle.execute_rest_json(payload))
        raise RustBindingsUnavailableError("rust runtime handle cannot execute REST envelopes")

    def execute_jsonrpc(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_request_payload(envelope)
        if hasattr(self._handle, "execute_jsonrpc_json"):
            return json.loads(self._handle.execute_jsonrpc_json(payload))
        raise RustBindingsUnavailableError(
            "rust runtime handle cannot execute JSON-RPC envelopes"
        )

    def execute_ws(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_request_payload(envelope)
        if hasattr(self._handle, "execute_ws_json"):
            return json.loads(self._handle.execute_ws_json(payload))
        raise RustBindingsUnavailableError("rust runtime handle cannot execute websocket envelopes")

    def execute_stream(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_request_payload(envelope)
        if hasattr(self._handle, "execute_stream_json"):
            return json.loads(self._handle.execute_stream_json(payload))
        raise RustBindingsUnavailableError("rust runtime handle cannot execute streaming envelopes")

    def execute_sse(self, envelope: Any) -> dict[str, object]:
        payload = _coerce_request_payload(envelope)
        if hasattr(self._handle, "execute_sse_json"):
            return json.loads(self._handle.execute_sse_json(payload))
        raise RustBindingsUnavailableError("rust runtime handle cannot execute SSE envelopes")

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


def create_runtime_from_compiled(plan: Any) -> RustRuntimeHandle:
    rust = _require_rust()
    handle = rust.create_runtime_handle(_coerce_compiled_plan(plan))
    return RustRuntimeHandle(handle)


def create_runtime(spec: Any) -> RustRuntimeHandle:
    from .compile import compile_app

    compiled = compile_app(spec)
    return create_runtime_from_compiled(compiled)
