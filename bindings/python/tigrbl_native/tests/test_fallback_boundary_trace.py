from __future__ import annotations

from tigrbl_native import (
    clear_ffi_boundary_events,
    compile_app,
    create_runtime,
    ffi_boundary_events,
    register_python_handler,
)


def test_source_fallback_records_boundary_events() -> None:
    clear_ffi_boundary_events()
    compiled = compile_app({"name": "demo"})
    handle = create_runtime({"name": "demo"})
    register_python_handler("demo.handler", lambda payload: payload)
    handle.begin_request("rest")
    handle.callback_fence("handler", "demo.handler")
    handle.finish_response("rest")

    assert compiled.startswith("compiled-spec:")
    assert "runtime handle" in handle.describe()

    events = ffi_boundary_events()
    names = [item["event"] for item in events]
    assert names[:3] == ["normalize_spec", "compile_spec", "normalize_spec"]
    assert "create_runtime_handle" in names
    assert "register_python_handler" in names
    assert names[-4:] == [
        "request_entry",
        "callback_fence_enter",
        "callback_fence_exit",
        "response_exit",
    ]
