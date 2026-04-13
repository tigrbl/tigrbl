from __future__ import annotations

import json
from typing import Any


def _coerce_spec_dict(spec: Any) -> dict[str, Any]:
    if isinstance(spec, str):
        payload = json.loads(spec)
    else:
        payload = json.loads(json.dumps(spec, sort_keys=True))
    if not isinstance(payload, dict):
        raise TypeError("native parity contract requires a mapping spec")
    return payload


def _family_from_transport(transport: str, exchange: str) -> str:
    if transport in {"ws", "wss", "webtransport"}:
        return "bidirectional"
    if exchange == "server_stream":
        return "server_stream"
    return "request_response"


def _transport_from_binding(binding: dict[str, Any], op: dict[str, Any]) -> str:
    explicit = binding.get("transport")
    if isinstance(explicit, str) and explicit:
        return explicit
    route = str(op.get("route") or binding.get("path") or "")
    exchange = str(op.get("exchange", "request_response"))
    if route.startswith("/rpc"):
        return "jsonrpc"
    if exchange == "server_stream":
        return "sse"
    if exchange == "bidirectional_stream":
        return "ws"
    return "rest"


def _phase_plan(op: dict[str, Any], transport: str) -> list[str]:
    tx_scope = str(op.get("tx_scope", "inherit"))
    exchange = str(op.get("exchange", "request_response"))
    phases = ["INGRESS_BEGIN", "INGRESS_DISPATCH", "PRE_HANDLER", "HANDLER", "POST_HANDLER"]
    if tx_scope != "none":
        phases.insert(2, "START_TX")
        phases.append("END_TX")
    if transport in {"sse", "ws", "wss", "webtransport"} or exchange != "request_response":
        phases.append("POST_EMIT")
    phases.append("POST_RESPONSE")
    return phases


def build_parity_snapshot(spec: Any) -> dict[str, Any]:
    payload = _coerce_spec_dict(spec)
    bindings = payload.get("bindings", [])
    if not isinstance(bindings, list):
        raise TypeError("native parity contract requires spec['bindings'] to be a list")

    routes: list[dict[str, Any]] = []
    opviews: list[dict[str, Any]] = []
    phase_plans: dict[str, list[str]] = {}
    openapi_paths: list[str] = []
    openrpc_methods: list[str] = []
    asyncapi_channels: list[str] = []

    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        alias = str(binding.get("alias") or "")
        op = binding.get("op", {})
        if not isinstance(op, dict):
            op = {}
        target = str(op.get("target") or op.get("name") or "custom")
        route = op.get("route") or binding.get("path")
        exchange = str(op.get("exchange", "request_response"))
        tx_scope = str(op.get("tx_scope", "inherit"))
        subevents = tuple(str(item) for item in op.get("subevents", []) or ())
        transport = _transport_from_binding(binding, op)
        family = str(binding.get("family") or _family_from_transport(transport, exchange))
        hooks = binding.get("hooks", [])
        hook_count = len(hooks) if isinstance(hooks, list) else 0

        route_item = {
            "alias": alias,
            "target": target,
            "route": route,
            "transport": transport,
            "exchange": exchange,
            "family": family,
        }
        routes.append(route_item)
        opviews.append(
            {
                "alias": alias,
                "target": target,
                "route": route,
                "exchange": exchange,
                "tx_scope": tx_scope,
                "family": family,
                "subevents": list(subevents),
                "hook_count": hook_count,
            }
        )
        phase_plans[alias] = _phase_plan(op, transport)

        if route and transport in {"rest", "jsonrpc"} and exchange == "request_response":
            openapi_paths.append(str(route))
        openrpc_methods.append(alias)
        if exchange != "request_response":
            asyncapi_channels.append(str(route or alias))

    return {
        "app_name": str(payload.get("name", "")),
        "routes": routes,
        "opviews": opviews,
        "phase_plans": phase_plans,
        "packed_plan": {
            "segments": len(routes),
            "hot_paths": 1 if routes else 0,
            "fused_steps": len(routes),
        },
        "docs": {
            "openapi_paths": openapi_paths,
            "openrpc_methods": openrpc_methods,
            "asyncapi_channels": asyncapi_channels,
        },
    }


def transport_trace(
    transport: str,
    *,
    include_hook: bool = False,
    include_error: bool = False,
    include_docs: bool = False,
) -> list[dict[str, Any]]:
    transport = str(transport).lower()
    if transport not in {"rest", "jsonrpc", "sse", "ws", "wss", "webtransport"}:
        raise ValueError(f"unsupported transport for parity trace: {transport}")

    events: list[dict[str, Any]] = [{"event": "request_entry", "transport": transport}]
    if transport == "rest":
        events.append({"event": "route_match", "transport": transport})
    elif transport == "jsonrpc":
        events.append({"event": "rpc_envelope_parse", "transport": transport})
    elif transport == "sse":
        events.append({"event": "stream_open", "transport": transport})
    else:
        events.append({"event": "channel_open", "transport": transport})

    if include_hook:
        events.append({"event": "callback_fence_enter", "transport": transport, "kind": "hook"})
        events.append({"event": "callback_fence_exit", "transport": transport, "kind": "hook"})

    events.append({"event": "handler_dispatch", "transport": transport})

    if include_error:
        events.append({"event": "error_map", "transport": transport})

    if include_docs:
        events.append({"event": "docs_emit", "transport": transport})

    if transport in {"sse", "ws", "wss", "webtransport"}:
        events.append({"event": "post_emit", "transport": transport})
    events.append({"event": "response_exit", "transport": transport})
    return events
