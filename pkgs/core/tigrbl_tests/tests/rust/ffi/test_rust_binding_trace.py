from __future__ import annotations

from tigrbl_runtime.rust import clear_ffi_boundary_events, create_runtime, ffi_boundary_events


def test_rust_runtime_trace_records_entry_and_response_exit() -> None:
    clear_ffi_boundary_events()
    handle = create_runtime({"name": "ffi-demo"})
    handle.begin_request("rpc")
    handle.finish_response("rpc")

    names = [item["event"] for item in ffi_boundary_events()]
    assert names[-2:] == ["request_entry", "response_exit"]
