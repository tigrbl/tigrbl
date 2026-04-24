from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import mem
from tigrbl.types import Column, String

from tigrbl_runtime import Runtime


RUST_EXECUTOR_ENTRYPOINTS = ("rust_handle", "runtime_execute_rust")

REQUEST_SEQUENCE: tuple[dict[str, Any], ...] = (
    {
        "transport": "rest",
        "operation": "widgets.create",
        "method": "POST",
        "path": "/widgets",
        "body": {"id": "w1", "name": "Ada"},
    },
    {
        "transport": "rest",
        "operation": "widgets.read",
        "method": "GET",
        "path": "/widgets/w1",
        "rust_path": "/widgets/{item_id}",
        "path_params": {"id": "w1"},
    },
    {
        "transport": "rest",
        "operation": "widgets.list",
        "method": "GET",
        "path": "/widgets",
    },
    {
        "transport": "jsonrpc",
        "operation": "widgets.create",
        "method": "POST",
        "path": "/rpc",
        "body": {"id": "w2", "name": "Bob"},
        "rpc_id": 1,
    },
    {
        "transport": "jsonrpc",
        "operation": "widgets.read",
        "method": "POST",
        "path": "/rpc",
        "path_params": {"id": "w2"},
        "rpc_id": 2,
    },
    {
        "transport": "jsonrpc",
        "operation": "widgets.list",
        "method": "POST",
        "path": "/rpc",
        "rpc_id": 3,
    },
)


def _registered_python_executor_names() -> tuple[str, ...]:
    return tuple(Runtime().executors)


def _make_widget_model(label: str) -> type[TableBase]:
    normalized = label.lower().replace(".", "_").replace("-", "_")
    attrs = {
        "__module__": __name__,
        "__tablename__": f"executor_parity_widget_{normalized}",
        "__allow_unmapped__": True,
        "id": Column(String, primary_key=True),
        "name": Column(String, nullable=False),
        "__tigrbl_ops__": (
            OpSpec(
                alias="widgets.create",
                target="create",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("POST",),
                        path="/widgets",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.create",
                    ),
                ),
            ),
            OpSpec(
                alias="widgets.read",
                target="read",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("GET",),
                        path="/widgets/{item_id}",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.read",
                    ),
                ),
            ),
            OpSpec(
                alias="widgets.list",
                target="list",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("GET",),
                        path="/widgets",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.list",
                    ),
                ),
            ),
        ),
    }
    return type("ExecutorParityWidget", (TableBase,), attrs)


def _rust_spec() -> dict[str, Any]:
    bindings: list[dict[str, Any]] = []
    for target, transport, path in (
        ("create", "rest", "/widgets"),
        ("read", "rest", "/widgets/{item_id}"),
        ("list", "rest", "/widgets"),
        ("create", "jsonrpc", "/rpc"),
        ("read", "jsonrpc", "/rpc"),
        ("list", "jsonrpc", "/rpc"),
    ):
        alias = f"widgets.{target}"
        bindings.append(
            {
                "alias": alias,
                "transport": transport,
                "path": path,
                "op": {"name": alias, "kind": target, "route": path},
                "table": {"name": "widgets"},
            }
        )
    return {"name": "executor-parity-demo", "bindings": bindings}


def _normalize_record(
    request: Mapping[str, Any],
    response: Mapping[str, Any],
) -> dict[str, Any]:
    record = {
        "transport": request["transport"],
        "operation": request["operation"],
        "body": response["body"],
    }
    if request["transport"] == "rest":
        record["status"] = response["status"]
    return record


async def _run_python_executor(executor_name: str) -> list[dict[str, Any]]:
    model = _make_widget_model(executor_name)
    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    app._runtime_default_executor = executor_name
    app.include_table(model)
    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized

    results: list[dict[str, Any]] = []
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        for request in REQUEST_SEQUENCE:
            if request["transport"] == "jsonrpc":
                response = await client.post(
                    "/rpc",
                    json={
                        "jsonrpc": "2.0",
                        "method": request["operation"],
                        "params": dict(
                            request.get("body") or request.get("path_params") or {}
                        ),
                        "id": request["rpc_id"],
                    },
                )
                payload = response.json()
                assert "error" not in payload, payload
                results.append(
                    _normalize_record(
                        request,
                        {"status": response.status_code, "body": payload["result"]},
                    )
                )
                continue

            response = await client.request(
                request["method"],
                request["path"],
                json=request.get("body"),
            )
            results.append(
                _normalize_record(
                    request,
                    {"status": response.status_code, "body": response.json()},
                )
            )

    return results


def _rust_envelope(request: Mapping[str, Any]) -> dict[str, Any]:
    envelope = {
        "operation": request["operation"],
        "transport": request["transport"],
        "path": request.get("rust_path", request["path"]),
        "method": request["method"],
    }
    if "body" in request:
        envelope["body"] = request["body"]
    if "path_params" in request:
        envelope["path_params"] = request["path_params"]
    return envelope


def _run_rust_executor(entrypoint: str) -> list[dict[str, Any]]:
    runtime = Runtime(executor_backend="rust")
    handle = runtime.rust_handle(_rust_spec())
    results: list[dict[str, Any]] = []

    for request in REQUEST_SEQUENCE:
        envelope = _rust_envelope(request)
        if entrypoint == "rust_handle":
            if request["transport"] == "rest":
                response = handle.execute_rest(envelope)
            else:
                response = handle.execute_jsonrpc(envelope)
        elif entrypoint == "runtime_execute_rust":
            response = runtime.execute_rust(envelope, handle=handle)
        else:  # pragma: no cover - guards the local matrix declaration
            raise AssertionError(f"unknown rust executor entrypoint: {entrypoint}")
        results.append(_normalize_record(request, response))

    return results


@pytest.mark.asyncio
async def test_same_inputs_yield_same_results_across_python_and_rust_executors() -> None:
    observed: dict[str, list[dict[str, Any]]] = {}
    for executor_name in _registered_python_executor_names():
        observed[f"python:{executor_name}"] = await _run_python_executor(executor_name)
    for entrypoint in RUST_EXECUTOR_ENTRYPOINTS:
        observed[f"rust:{entrypoint}"] = _run_rust_executor(entrypoint)

    baseline_name, baseline_results = next(iter(observed.items()))
    for executor_name, results in observed.items():
        assert results == baseline_results, (
            f"{executor_name} diverged from {baseline_name}"
        )
