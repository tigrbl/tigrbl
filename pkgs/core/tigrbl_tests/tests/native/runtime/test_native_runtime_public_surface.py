from __future__ import annotations

from tigrbl_runtime import (
    build_native_runtime,
    clear_native_boundary_events,
    native_boundary_events,
    transport_parity_trace,
)


def test_native_runtime_surface_exposes_boundary_trace_helpers() -> None:
    clear_native_boundary_events()
    handle = build_native_runtime({"name": "runtime-demo"})
    handle.begin_request("rest")
    handle.callback_fence("hook", "pre_handler")
    handle.finish_response("rest")

    names = [item["event"] for item in native_boundary_events()]
    assert names[-4:] == [
        "request_entry",
        "callback_fence_enter",
        "callback_fence_exit",
        "response_exit",
    ]
    assert transport_parity_trace("rest", include_hook=True)[-1]["event"] == "response_exit"
