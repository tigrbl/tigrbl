from __future__ import annotations

from tigrbl_runtime import (
    Runtime,
    clear_rust_boundary_events,
    rust_boundary_events,
    rust_transport_trace,
)


def test_rust_runtime_surface_exposes_boundary_trace_helpers() -> None:
    clear_rust_boundary_events()
    handle = Runtime(executor_backend="rust").rust_handle({"name": "runtime-demo"})
    handle.begin_request("rest")
    handle.callback_fence("hook", "pre_handler")
    handle.finish_response("rest")

    names = [item["event"] for item in rust_boundary_events()]
    assert names[-4:] == [
        "request_entry",
        "callback_fence_enter",
        "callback_fence_exit",
        "response_exit",
    ]
    assert rust_transport_trace("rest", include_hook=True)[-1]["event"] == "response_exit"
