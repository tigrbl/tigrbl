from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from tigrbl_core.config.constants import (
    DEFAULT_ROOT_RESPONSE,
    TIGRBL_DEFAULT_ROOT_ALIAS,
)

from ._parity_contract import build_parity_snapshot as _build_parity_snapshot
from ._parity_contract import transport_trace as _transport_trace

_BOUNDARY_EVENTS: list[dict[str, Any]] = []
_SEQ = 0


def _record(event: str, **payload: Any) -> dict[str, Any]:
    global _SEQ
    item = {"seq": _SEQ, "event": event, **payload}
    _BOUNDARY_EVENTS.append(item)
    _SEQ += 1
    return item


def ffi_boundary_events() -> list[dict[str, Any]]:
    return [dict(item) for item in _BOUNDARY_EVENTS]


def clear_ffi_boundary_events() -> None:
    _BOUNDARY_EVENTS.clear()


def rust_available() -> bool:
    return True


def compiled_extension_available() -> bool:
    return False


def _normalize_path(path: Any) -> str:
    return str(path or "/").rstrip("/") or "/"


def _is_default_root_request(transport: str, request: dict[str, Any]) -> bool:
    method = str(request.get("method") or "GET").upper()
    return (
        transport == "rest"
        and method == "GET"
        and _normalize_path(request.get("path")) == "/"
    )


def _has_explicit_root_binding(bindings: list[dict[str, Any]]) -> bool:
    return any(
        binding.get("transport") == "rest"
        and _normalize_path(binding.get("path")) == "/"
        and binding.get("alias") != TIGRBL_DEFAULT_ROOT_ALIAS
        for binding in bindings
    )


def normalize_spec(spec_json: str) -> str:
    trimmed = str(spec_json or "").strip()
    if not trimmed:
        raise RuntimeError("empty spec payload")
    normalized = json.dumps(json.loads(trimmed), sort_keys=True)
    _record("normalize_spec", size=len(normalized))
    return normalized


def compile_spec(spec_json: str) -> str:
    spec = json.loads(normalize_spec(spec_json))
    engine = ((spec.get("engines") or [{}])[0]) or {}
    engine_kind = engine.get("kind", "inmemory")
    engine_language = engine.get("language", "rust")
    engine_callback = engine.get("callback")
    engine_options = dict(engine.get("options") or {})
    callbacks = [item.get("name", "") for item in spec.get("callbacks", [])]
    bindings = []
    routes = []
    for binding in spec.get("bindings", []):
        op = binding.get("op", {})
        path = op.get("route") or binding.get("path") or f"/{binding.get('alias', '')}"
        transport = binding.get("transport", "rest")
        op_kind = op.get("kind") or op.get("target") or op.get("name", "create")
        method = {
            "rest": {
                "create": "POST",
                "read": "GET",
                "list": "GET",
                "delete": "DELETE",
                "replace": "PUT",
                "update": "PATCH",
                "merge": "PATCH",
            }.get(op_kind, "POST"),
            "jsonrpc": "POST",
            "ws": "MESSAGE",
            "sse": "GET",
            "stream": "GET",
        }.get(transport, "POST")
        item = {
            "alias": binding.get("alias", ""),
            "op_name": op.get("name") or op.get("target", ""),
            "op_kind": op_kind,
            "transport": transport,
            "family": binding.get("family", transport),
            "framing": binding.get("framing"),
            "path": path,
            "method": method,
            "method_name": binding.get("alias", "") if transport == "jsonrpc" else (op.get("name") or op.get("target", "")),
            "exchange": op.get("exchange", "request_response"),
            "tx_scope": op.get("tx_scope", "inherit"),
            "subevents": list(op.get("subevents", []) or []),
            "hooks": [hook.get("name") or hook.get("phase", "") for hook in binding.get("hooks", [])],
            "callback_fences": [
                f"hook:{hook.get('name') or hook.get('phase', '')}" for hook in binding.get("hooks", [])
            ],
            "table": (binding.get("table") or {}).get("name", binding.get("alias", "")),
            "engine_kind": engine_kind,
            "engine_language": engine_language,
            "engine_callback": engine_callback,
            "engine_options": deepcopy(engine_options),
        }
        bindings.append(item)
        routes.append(
            {
                "transport": transport,
                "family": item["family"],
                "path": path,
                "method": method,
                "method_name": item["method_name"],
                "binding_alias": item["alias"],
                "op_name": item["op_name"],
            }
        )
    payload = {
        "app_name": spec.get("name", ""),
        "title": spec.get("title", spec.get("name", "")),
        "version": spec.get("version", "0.1.0"),
        "engine_kind": engine_kind,
        "engine_options": deepcopy(engine_options),
        "binding_count": len(bindings),
        "route_count": len(routes),
        "callbacks": callbacks,
        "runtime": deepcopy(spec.get("runtime", {})),
        "metadata": deepcopy(spec.get("metadata", {})),
        "bindings": bindings,
        "routes": routes,
        "packed": {
            "segments": len(bindings),
            "hot_paths": min(len(bindings), 1),
            "fused_steps": len(bindings),
            "routes": len(routes),
        },
    }
    _record("compile_spec", binding_count=len(bindings), route_count=len(routes))
    return json.dumps(payload, sort_keys=True)


@dataclass(slots=True)
class RuntimeHandle:
    plan_json_payload: str
    description_text: str = field(init=False)
    _plan: dict[str, Any] = field(init=False)
    _tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self._plan = json.loads(self.plan_json_payload)
        self.description_text = (
            f"runtime handle for {len(self._plan.get('bindings', []))} binding(s) in app {self._plan.get('app_name', '')}"
        )
        _record("create_runtime_handle", app_name=self._plan.get("app_name", ""))

    def describe(self) -> str:
        return self.description_text

    def plan_json(self) -> str:
        return json.dumps(self._plan, sort_keys=True)

    def execute_rest_json(self, request_json: str) -> str:
        request = json.loads(request_json)
        _record("request_entry", transport="rest", operation=request.get("operation"))
        response = self._execute("rest", request)
        _record("response_exit", transport="rest", status=response["status"])
        return json.dumps(response, sort_keys=True)

    def execute_jsonrpc_json(self, request_json: str) -> str:
        request = json.loads(request_json)
        _record("request_entry", transport="jsonrpc", operation=request.get("operation"))
        response = self._execute("jsonrpc", request)
        _record("response_exit", transport="jsonrpc", status=response["status"])
        return json.dumps(response, sort_keys=True)

    def execute_ws_json(self, request_json: str) -> str:
        request = json.loads(request_json)
        _record("request_entry", transport="ws", operation=request.get("operation"))
        response = self._execute("ws", request)
        _record("response_exit", transport="ws", status=response["status"])
        return json.dumps(response, sort_keys=True)

    def execute_stream_json(self, request_json: str) -> str:
        request = json.loads(request_json)
        _record("request_entry", transport="stream", operation=request.get("operation"))
        response = self._execute("stream", request)
        _record("response_exit", transport="stream", status=response["status"])
        return json.dumps(response, sort_keys=True)

    def execute_sse_json(self, request_json: str) -> str:
        request = json.loads(request_json)
        _record("request_entry", transport="sse", operation=request.get("operation"))
        response = self._execute("sse", request)
        _record("response_exit", transport="sse", status=response["status"])
        return json.dumps(response, sort_keys=True)

    def begin_request(self, transport: str = "rest") -> None:
        _record("request_entry", transport=transport)

    def callback_fence(self, kind: str, name: str) -> None:
        _record("callback_fence_enter", kind=kind, name=name)
        _record("callback_fence_exit", kind=kind, name=name)

    def finish_response(self, transport: str = "rest") -> None:
        _record("response_exit", transport=transport)

    def ffi_events(self) -> list[dict[str, Any]]:
        return ffi_boundary_events()

    def _execute(self, transport: str, request: dict[str, Any]) -> dict[str, Any]:
        if _is_default_root_request(
            transport, request
        ) and not _has_explicit_root_binding(self._plan["bindings"]):
            return {"status": 200, "headers": {}, "body": dict(DEFAULT_ROOT_RESPONSE)}

        binding = next(
            (
                binding
                for binding in self._plan["bindings"]
                if binding["transport"] == transport
                and (
                    binding["alias"] == request.get("operation")
                    or binding["op_name"] == request.get("operation")
                    or binding["path"] == request.get("path")
                )
            ),
            None,
        )
        if binding is None:
            raise RuntimeError("no matching rust binding")
        if binding.get("engine_language", "rust") != "rust" and not binding.get("engine_callback"):
            raise RuntimeError("catastrophic rust runtime failure: python-backed engine missing callback")

        table = self._tables.setdefault(binding["table"], [])
        kind = binding["op_kind"]
        body = request.get("body") or {}
        row_id = (
            (request.get("path_params") or {}).get("id")
            or (request.get("query_params") or {}).get("id")
            or body.get("id")
        )
        if kind == "create":
            table.append(deepcopy(body))
            return {"status": 201, "headers": {}, "body": deepcopy(body)}
        if kind == "list":
            return {"status": 200, "headers": {}, "body": deepcopy(table)}
        row = next((item for item in table if item.get("id") == row_id), None)
        if row is None:
            return {"status": 404, "headers": {}, "body": {"error": "not found"}}
        if kind == "read":
            return {"status": 200, "headers": {}, "body": deepcopy(row)}
        if kind in {"update", "replace"}:
            row.clear()
            row.update(deepcopy(body))
            return {"status": 200, "headers": {}, "body": deepcopy(row)}
        if kind == "merge":
            row.update(deepcopy(body))
            return {"status": 200, "headers": {}, "body": deepcopy(row)}
        if kind == "delete":
            table.remove(row)
            return {"status": 200, "headers": {}, "body": deepcopy(row)}
        return {"status": 501, "headers": {}, "body": {"error": f"unsupported op {kind}"}}


def create_runtime_handle(plan_json: str) -> RuntimeHandle:
    return RuntimeHandle(plan_json)


def _descriptor(kind: str, name: str) -> str:
    return f"{kind}:{name}"


def register_python_callback(name: str) -> str:
    _record("register_python_callback", name=name)
    return _descriptor("python-callback", name)


def register_python_atom(name: str) -> str:
    _record("register_python_atom", name=name)
    return _descriptor("python-atom", name)


def register_python_hook(name: str) -> str:
    _record("register_python_hook", name=name)
    return _descriptor("python-hook", name)


def register_python_handler(name: str) -> str:
    _record("register_python_handler", name=name)
    return _descriptor("python-handler", name)


def register_python_engine(name: str) -> str:
    _record("register_python_engine", name=name)
    return _descriptor("python-engine", name)


def build_parity_snapshot(spec: Any) -> dict[str, Any]:
    payload = _build_parity_snapshot(spec)
    _record("parity_snapshot", bindings=len(payload.get("routes", ())))
    return payload


def transport_trace(
    transport: str,
    *,
    include_hook: bool = False,
    include_error: bool = False,
    include_docs: bool = False,
) -> list[dict[str, Any]]:
    trace = _transport_trace(
        transport,
        include_hook=include_hook,
        include_error=include_error,
        include_docs=include_docs,
    )
    _record(
        "transport_trace",
        transport=transport,
        include_hook=include_hook,
        include_error=include_error,
        include_docs=include_docs,
    )
    return trace
