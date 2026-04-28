from __future__ import annotations

from typing import Any

from tigrbl_core._spec.binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    TransportBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.op_spec import OpSpec


def binding_family(binding: TransportBindingSpec) -> str:
    if isinstance(binding, WebTransportBindingSpec):
        return "session"
    if isinstance(binding, WsBindingSpec):
        return "socket"
    if isinstance(binding, (HttpStreamBindingSpec, SseBindingSpec)):
        return "stream"
    return "request"


def binding_surface(binding: TransportBindingSpec) -> dict[str, Any]:
    surface = {
        "proto": getattr(binding, "proto", None),
        "path": getattr(binding, "path", None),
        "rpcMethod": getattr(binding, "rpc_method", None),
        "framing": getattr(binding, "framing", None),
        "exchange": getattr(binding, "exchange", None),
        "family": binding_family(binding),
    }
    if isinstance(binding, (HttpRestBindingSpec, HttpStreamBindingSpec, SseBindingSpec)):
        surface["methods"] = tuple(getattr(binding, "methods", ()) or ())
    if isinstance(binding, WsBindingSpec):
        surface["subprotocols"] = tuple(getattr(binding, "subprotocols", ()) or ())
    if isinstance(binding, HttpJsonRpcBindingSpec):
        surface["methods"] = None
    return surface


def op_family(spec: OpSpec) -> str:
    target = str(getattr(spec, "target", "custom") or "custom")
    if target.startswith("bulk_"):
        return "bulk"
    if target == "custom":
        return "custom"
    return "crud"


def op_surface(spec: OpSpec) -> dict[str, Any]:
    return {
        "bindings": [
            binding_surface(binding)
            for binding in tuple(getattr(spec, "bindings", ()) or ())
        ],
        "exchange": getattr(spec, "exchange", None),
        "txScope": getattr(spec, "tx_scope", None),
        "family": op_family(spec),
        "subevents": list(tuple(getattr(spec, "subevents", ()) or ())),
    }


def auth_surface(security: list[dict[str, list[str]]]) -> dict[str, Any]:
    """Describe the generated operation auth policy in documentation output."""

    if security:
        return {
            "policy": "protected",
            "public": False,
            "security": security,
        }
    return {
        "policy": "public-by-default",
        "public": True,
        "security": [],
    }


__all__ = [
    "auth_surface",
    "binding_family",
    "binding_surface",
    "op_family",
    "op_surface",
]
