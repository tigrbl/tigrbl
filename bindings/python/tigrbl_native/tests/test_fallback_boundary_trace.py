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
    spec = {
        "name": "demo",
        "bindings": [
            {
                "alias": "users.create",
                "transport": "rest",
                "path": "/users",
                "op": {"name": "create", "kind": "create", "route": "/users"},
                "table": {"name": "users"},
            }
        ],
    }
    compiled = compile_app(spec)
    handle = create_runtime(spec)
    register_python_handler("demo.handler", lambda payload: payload)
    response = handle.execute_rest(
        {
            "operation": "users.create",
            "transport": "rest",
            "path": "/users",
            "method": "POST",
            "body": {"id": "u1", "name": "Ada"},
        }
    )
    handle.callback_fence("handler", "demo.handler")

    assert compiled["binding_count"] == 1
    assert "runtime handle" in handle.describe()
    assert response["status"] == 201
    assert response["body"]["id"] == "u1"

    events = ffi_boundary_events()
    names = [item["event"] for item in events]
    assert names[:3] == ["normalize_spec", "compile_spec", "normalize_spec"]
    assert "create_runtime_handle" in names
    assert "register_python_handler" in names
    assert "request_entry" in names
    assert "response_exit" in names
    assert names[-2:] == ["callback_fence_enter", "callback_fence_exit"]
