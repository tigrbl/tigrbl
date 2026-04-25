from __future__ import annotations

from tigrbl_runtime import (
    Runtime,
    clear_rust_boundary_events,
    rust_boundary_events,
    rust_transport_trace,
)
from tigrbl_core.config.constants import DEFAULT_ROOT_RESPONSE, TIGRBL_DEFAULT_ROOT_ALIAS


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


def test_rust_runtime_returns_default_root_without_bindings() -> None:
    clear_rust_boundary_events()
    handle = Runtime(executor_backend="rust").rust_handle({"name": "runtime-demo"})
    aliases = {binding["alias"] for binding in handle.plan().get("bindings", [])}

    response = handle.execute_rest(
        {"transport": "rest", "path": "/", "method": "GET"}
    )
    names = [item["event"] for item in rust_boundary_events()]

    assert TIGRBL_DEFAULT_ROOT_ALIAS in aliases
    assert response == {"status": 200, "headers": {}, "body": dict(DEFAULT_ROOT_RESPONSE)}
    assert names[-2:] == ["request_entry", "response_exit"]


def test_rust_runtime_explicit_root_binding_overrides_default_root() -> None:
    handle = Runtime(executor_backend="rust").rust_handle(
        {
            "name": "runtime-demo",
            "bindings": [
                {
                    "alias": "root.list",
                    "transport": "rest",
                    "path": "/",
                    "op": {"name": "list", "kind": "list", "route": "/"},
                    "table": {"name": "root"},
                }
            ],
        }
    )
    aliases = {binding["alias"] for binding in handle.plan().get("bindings", [])}

    response = handle.execute_rest(
        {"transport": "rest", "path": "/", "method": "GET"}
    )

    assert TIGRBL_DEFAULT_ROOT_ALIAS not in aliases
    assert response == {"status": 200, "headers": {}, "body": []}
