from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import raise_rust_deprecated


@dataclass(slots=True)
class RustRuntimeHandle:
    _handle: Any = None

    def describe(self) -> str:
        raise_rust_deprecated("RustRuntimeHandle.describe")

    def plan(self) -> dict[str, object]:
        raise_rust_deprecated("RustRuntimeHandle.plan")

    def execute_rest(self, envelope: Any) -> dict[str, object]:
        del envelope
        raise_rust_deprecated("RustRuntimeHandle.execute_rest")

    def execute_jsonrpc(self, envelope: Any) -> dict[str, object]:
        del envelope
        raise_rust_deprecated("RustRuntimeHandle.execute_jsonrpc")

    def execute_ws(self, envelope: Any) -> dict[str, object]:
        del envelope
        raise_rust_deprecated("RustRuntimeHandle.execute_ws")

    def execute_stream(self, envelope: Any) -> dict[str, object]:
        del envelope
        raise_rust_deprecated("RustRuntimeHandle.execute_stream")

    def execute_sse(self, envelope: Any) -> dict[str, object]:
        del envelope
        raise_rust_deprecated("RustRuntimeHandle.execute_sse")

    def begin_request(self, transport: str = "rest") -> None:
        del transport
        raise_rust_deprecated("RustRuntimeHandle.begin_request")

    def callback_fence(self, kind: str, name: str) -> None:
        del kind, name
        raise_rust_deprecated("RustRuntimeHandle.callback_fence")

    def finish_response(self, transport: str = "rest") -> None:
        del transport
        raise_rust_deprecated("RustRuntimeHandle.finish_response")

    def ffi_events(self) -> list[dict[str, object]]:
        raise_rust_deprecated("RustRuntimeHandle.ffi_events")


def create_runtime_from_compiled(plan: Any) -> RustRuntimeHandle:
    del plan
    raise_rust_deprecated("tigrbl_runtime.rust.create_runtime_from_compiled")


def create_runtime(spec: Any) -> RustRuntimeHandle:
    del spec
    raise_rust_deprecated("tigrbl_runtime.rust.create_runtime")
