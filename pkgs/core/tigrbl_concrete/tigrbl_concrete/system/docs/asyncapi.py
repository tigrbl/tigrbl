from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete._concrete._routing import register_http_route
from tigrbl_core._spec.binding_spec import (
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from .surface import binding_family, op_surface

ASYNCAPI_VERSION = "2.6.0"


def _iter_declared_transport_bindings(router: Any):
    tables = getattr(router, "tables", {}) or {}
    values = tables.values() if isinstance(tables, dict) else tables
    for table in values:
        ops = getattr(getattr(table, "ops", None), "all", ()) or ()
        for spec in ops:
            for binding in tuple(getattr(spec, "bindings", ()) or ()):
                if isinstance(binding, (WsBindingSpec, WebTransportBindingSpec, SseBindingSpec)):
                    yield spec, binding


def _binding_operation(binding: Any) -> str:
    if isinstance(binding, SseBindingSpec):
        return "subscribe"
    return "receive"


def _build_asyncapi_spec(router: Any) -> dict[str, Any]:
    channels: dict[str, Any] = {}
    for spec, binding in _iter_declared_transport_bindings(router):
        operation_name = _binding_operation(binding)
        entry = channels.setdefault(binding.path, {})
        op_entry: dict[str, Any] = {"operationId": getattr(spec, "alias", binding.path)}
        summary = getattr(spec, "summary", None)
        description = getattr(spec, "description", None)
        if isinstance(summary, str) and summary:
            op_entry["summary"] = summary
        if isinstance(description, str) and description:
            op_entry["description"] = description
        op_entry["bindings"] = {
            str(getattr(binding, "proto", "unknown")): {
                "exchange": getattr(spec, "exchange", None),
                "framing": getattr(binding, "framing", None),
                "family": binding_family(binding),
            }
        }
        op_entry["x-tigrbl-surface"] = op_surface(spec)
        entry[operation_name] = op_entry
    return {
        "asyncapi": ASYNCAPI_VERSION,
        "info": {
            "title": getattr(router, "title", "API"),
            "version": getattr(router, "version", "0.1.0"),
        },
        "channels": channels,
    }


def _mount_asyncapi(
    router: Any,
    *,
    path: str = "/asyncapi.json",
    name: str = "__asyncapi__",
) -> Any:
    normalized_path = path if str(path).startswith("/") else f"/{path}"

    def _asyncapi_handler(_request: Any) -> Response:
        return Response.json(_build_asyncapi_spec(router))

    register_http_route(router, path=normalized_path, methods=("GET",), alias=name, endpoint=_asyncapi_handler)
    router.add_route(
        normalized_path,
        _asyncapi_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["ASYNCAPI_VERSION", "_build_asyncapi_spec", "_mount_asyncapi"]
