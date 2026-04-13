from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

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


def native_available() -> bool:
    return True


def compiled_extension_available() -> bool:
    return False


def normalize_spec(spec_json: str) -> str:
    trimmed = str(spec_json or "").strip()
    if not trimmed:
        raise RuntimeError("empty spec payload")
    normalized = json.dumps(json.loads(trimmed), sort_keys=True)
    _record("normalize_spec", size=len(normalized))
    return normalized


def compile_spec(spec_json: str) -> str:
    spec = json.loads(normalize_spec(spec_json))
    bindings = []
    routes = []
    engine_kind = ((spec.get("engines") or [{}])[0]).get("kind", "inmemory")
    for binding in spec.get("bindings", []):
        op = binding.get("op", {})
        path = op.get("route") or binding.get("path") or f"/{binding.get('alias', '')}"
        item = {
            "alias": binding.get("alias", ""),
            "op_name": op.get("name", ""),
            "op_kind": op.get("kind", op.get("name", "create")),
            "transport": binding.get("transport", "rest"),
            "path": path,
            "table": (binding.get("table") or {}).get("name", binding.get("alias", "")),
            "engine_kind": engine_kind,
        }
        bindings.append(item)
        routes.append(
            {
                "transport": item["transport"],
                "path": item["path"],
                "binding_alias": item["alias"],
                "op_name": item["op_name"],
            }
        )
    payload = {
        "description": f"compiled native plan for {spec.get('name', '')} with {len(bindings)} binding(s)",
        "app_name": spec.get("name", ""),
        "engine_kind": engine_kind,
        "binding_count": len(bindings),
        "route_count": len(routes),
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
    spec_json: str
    description_text: str = field(init=False)
    _plan: dict[str, Any] = field(init=False)
    _tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        normalized = normalize_spec(self.spec_json)
        self._plan = json.loads(compile_spec(normalized))
        self.description_text = (
            f"runtime handle for {self._plan['binding_count']} binding(s) in app {self._plan['app_name']}"
        )
        _record("create_runtime_handle", size=len(normalized))

    def describe(self) -> str:
        return self.description_text

    def plan_json(self) -> str:
        return json.dumps(
            {
                "app_name": self._plan["app_name"],
                "engine_kind": self._plan["engine_kind"],
                "bindings": self._plan["bindings"],
                "routes": self._plan["routes"],
                "packed": self._plan["packed"],
            },
            sort_keys=True,
        )

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
            raise RuntimeError("no matching native binding")

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


def create_runtime_handle(spec_json: str) -> RuntimeHandle:
    return RuntimeHandle(spec_json)


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
