from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_DECORATOR_BINDINGS: dict[str, dict[str, str]] = {
    "websocket_ctx": {
        "proto": "ws",
        "exchange": "bidirectional_stream",
        "framing": "text",
    },
    "sse_ctx": {
        "proto": "http.sse",
        "exchange": "server_stream",
        "framing": "sse",
    },
    "stream_ctx": {
        "proto": "http.stream",
        "exchange": "server_stream",
        "framing": "stream",
    },
    "webtransport_ctx": {
        "proto": "webtransport",
        "exchange": "bidirectional_stream",
        "framing": "webtransport",
    },
}


def lower_eventful_protocol_decorator(
    decorator: str,
    *,
    path: str,
    alias: str,
) -> dict[str, Any]:
    binding = dict(_DECORATOR_BINDINGS[decorator])
    binding["path"] = path
    return {
        "semantic_root": "op_ctx",
        "op_spec": {"alias": alias, "target": "custom"},
        "binding_specs": (binding,),
    }


def lower_subevent_ctx(
    *,
    family: str,
    subevent: str,
    handler_name: str,
) -> dict[str, str]:
    return {
        "kind": "subevent_handler",
        "family": family,
        "subevent": subevent,
        "handler_name": handler_name,
        "phase": "HANDLER",
    }


def validate_eventful_declaration(declaration: Mapping[str, Any]) -> None:
    if declaration.get("bypass_op_ctx"):
        raise ValueError("eventful decorator must lower through op_ctx")
    decorator = declaration.get("decorator")
    binding = declaration.get("binding")
    if decorator in _DECORATOR_BINDINGS and binding is not None:
        expected = _DECORATOR_BINDINGS[str(decorator)]["proto"]
        if str(binding) not in {expected, str(decorator).replace("_ctx", "")}:
            raise ValueError("binding declaration is ambiguous for eventful decorator")
    if declaration.get("duplicate_handler_name"):
        raise ValueError("subevent handler declaration is ambiguous")


def lower_realtime_verb(verb: str) -> dict[str, str]:
    return {
        "kind": "builtin_custom_handler",
        "semantic_root": "op_ctx",
        "handler_name": verb,
    }


def lower_on_mapping(*, family: str, on: Mapping[str, str]) -> tuple[dict[str, str], ...]:
    return tuple(
        lower_subevent_ctx(family=family, subevent=subevent, handler_name=handler)
        for subevent, handler in on.items()
    )


__all__ = [
    "lower_eventful_protocol_decorator",
    "lower_on_mapping",
    "lower_realtime_verb",
    "lower_subevent_ctx",
    "validate_eventful_declaration",
]
