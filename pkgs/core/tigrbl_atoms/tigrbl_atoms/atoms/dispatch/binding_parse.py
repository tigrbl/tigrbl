from __future__ import annotations

import json
import uuid
from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.DISPATCH_BINDING_PARSE


def _dispatch_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    obj = temp.setdefault("dispatch", {})
    if isinstance(obj, dict):
        return obj
    temp["dispatch"] = {}
    return temp["dispatch"]


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    dispatch = _dispatch_dict(ctx)
    temp = getattr(ctx, "temp", None)
    route = temp.setdefault("route", {}) if isinstance(temp, dict) else {}
    hot = temp.setdefault("hot", {}) if isinstance(temp, dict) else {}
    protocol = str(dispatch.get("binding_protocol", "") or "")
    body = getattr(ctx, "body", None)

    if isinstance(body, (bytes, bytearray)):
        parsed = hot.get("parsed_json") if isinstance(hot, dict) else None
        loaded = bool(hot.get("parsed_json_loaded")) if isinstance(hot, dict) else False
        if not loaded:
            try:
                parsed = json.loads(bytes(body).decode("utf-8"))
            except Exception:
                parsed = None
            if isinstance(hot, dict):
                hot["parsed_json"] = parsed
                hot["parsed_json_loaded"] = True
        body = parsed

    if not protocol and isinstance(body, list):
        endpoint = dispatch.get("endpoint") or route.get("endpoint")
        if not isinstance(endpoint, str) or not endpoint:
            dispatch["parsed_payload"] = body
            if isinstance(route, dict):
                route["payload"] = body
            return
        is_jsonrpc_batch = all(
            isinstance(item, Mapping) and item.get("jsonrpc") == "2.0" for item in body
        )
        if is_jsonrpc_batch:
            dispatch["rpc_batch"] = [dict(item) for item in body]
            dispatch["parsed_payload"] = dispatch["rpc_batch"]
            if isinstance(route, dict):
                route["payload"] = dispatch["rpc_batch"]
            return

    if protocol.endswith(".jsonrpc"):
        if isinstance(body, Mapping):
            endpoint = str(
                dispatch.get("endpoint")
                or route.get("endpoint")
                or ""
            )
            method = body.get("method")
            if isinstance(temp, dict):
                temp["jsonrpc_request_id"] = body.get("id")
            dispatch["endpoint"] = endpoint
            dispatch.setdefault(
                "binding_selector",
                f"{endpoint}:{method}" if isinstance(method, str) and method else method,
            )
            dispatch["rpc"] = dict(body)
            dispatch["rpc_method"] = method
            params = body.get("params", {})
            if isinstance(params, Mapping) and set(params) == {"params"}:
                dispatch.pop("binding_selector", None)
                egress = temp.setdefault("egress", {}) if isinstance(temp, dict) else {}
                if isinstance(egress, dict):
                    egress["transport_response"] = {
                        "status_code": 204,
                        "body": b"",
                    }
                if isinstance(route, dict):
                    route.pop("selector", None)
                    route["short_circuit"] = True
                    route["rpc_envelope"] = dict(body)
                return
            dispatch["parsed_payload"] = params
            if isinstance(route, dict):
                route["selector"] = dispatch.get("binding_selector")
                route["endpoint"] = endpoint
                route["rpc_envelope"] = dict(body)
        elif isinstance(body, list):
            dispatch["rpc_batch"] = [
                dict(item) if isinstance(item, Mapping) else item for item in body
            ]
            dispatch["parsed_payload"] = dispatch["rpc_batch"]
        if isinstance(route, dict):
            route["payload"] = body
    elif protocol.endswith(".rest"):
        if isinstance(body, (bytes, bytearray)):
            parsed = hot.get("parsed_json") if isinstance(hot, dict) else None
            loaded = bool(hot.get("parsed_json_loaded")) if isinstance(hot, dict) else False
            if not loaded:
                try:
                    parsed = json.loads(bytes(body).decode("utf-8"))
                except Exception:
                    parsed = None
                if isinstance(hot, dict):
                    hot["parsed_json"] = parsed
                    hot["parsed_json_loaded"] = True
            body = parsed
        payload: dict[str, object] = {}
        query = getattr(ctx, "query", None)
        if isinstance(query, Mapping):
            for k, v in query.items():
                # parse_qs returns lists; unwrap single-element lists
                if isinstance(v, list) and len(v) == 1:
                    payload[str(k)] = v[0]
                else:
                    payload[str(k)] = v
        path_params = dispatch.get("path_params")
        if isinstance(path_params, Mapping):
            payload.update({str(k): v for k, v in path_params.items()})
        if isinstance(body, list):
            # Bulk operation: inject path params into each item
            coerced_params = {}
            if isinstance(path_params, Mapping):
                for pk, pv in path_params.items():
                    if isinstance(pv, str):
                        try:
                            coerced_params[pk] = uuid.UUID(pv)
                        except (ValueError, AttributeError):
                            coerced_params[pk] = pv
                    else:
                        coerced_params[pk] = pv
            for idx, item in enumerate(body):
                if isinstance(item, Mapping):
                    merged = dict(coerced_params)
                    merged.update(item)
                    body[idx] = merged
            dispatch["parsed_payload"] = body
            if isinstance(route, dict):
                route["payload"] = body
                route["path_params"] = (
                    dict(path_params) if isinstance(path_params, Mapping) else {}
                )
        elif isinstance(body, Mapping):
            payload.update({str(k): v for k, v in body.items()})
            dispatch["parsed_payload"] = payload
            if isinstance(route, dict):
                route["payload"] = payload
        else:
            dispatch["parsed_payload"] = payload
            if isinstance(route, dict):
                route["payload"] = payload
    else:
        dispatch["parsed_payload"] = body
        if isinstance(route, dict):
            route["payload"] = body


class AtomImpl(Atom[Bound, Bound, Exception]):
    name = "dispatch.binding_parse"
    anchor = ANCHOR

    @staticmethod
    async def _execute_rpc_batch(
        ctx: Any, batch_payload: list[Any]
    ) -> list[dict[str, Any]]:
        router_or_app = getattr(ctx, "router", None) or getattr(ctx, "app", None)
        raw = getattr(ctx, "raw", None)
        scope = dict(getattr(raw, "scope", {}) or {})
        if scope:
            scope["method"] = "POST"
            headers = list(scope.get("headers", ()) or ())
            if not any(
                bytes(key).lower() == b"content-type"
                for key, _value in headers
                if isinstance(key, (bytes, bytearray))
            ):
                headers.append((b"content-type", b"application/json"))
            scope["headers"] = headers
        responses: list[dict[str, Any]] = []

        for item in batch_payload:
            if not isinstance(item, Mapping):
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    }
                )
                continue

            rpc_id = item.get("id")
            method = item.get("method")
            if not isinstance(method, str):
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": rpc_id,
                    }
                )
                continue

            if not callable(router_or_app) or not scope:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": "RPC invoker unavailable."},
                        },
                        "id": rpc_id,
                    }
                )
                continue

            body = json.dumps(dict(item), separators=(",", ":")).encode("utf-8")
            messages = [{"type": "http.request", "body": body, "more_body": False}]
            sent: list[dict[str, Any]] = []

            try:
                async def _receive() -> dict[str, Any]:
                    if messages:
                        return messages.pop(0)
                    return {"type": "http.request", "body": b"", "more_body": False}

                async def _send(message: dict[str, Any]) -> None:
                    sent.append(dict(message))

                await router_or_app(dict(scope), _receive, _send)
            except Exception as exc:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": str(exc)},
                        },
                        "id": rpc_id,
                    }
                )
                continue

            body_parts = [
                message.get("body", b"")
                for message in sent
                if message.get("type") == "http.response.body"
            ]
            response_body = b"".join(
                bytes(part) if isinstance(part, (bytes, bytearray)) else b""
                for part in body_parts
            )
            if not response_body:
                continue
            try:
                decoded = json.loads(response_body.decode("utf-8"))
            except Exception:
                decoded = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": {"detail": response_body.decode("utf-8", errors="replace")},
                    },
                    "id": rpc_id,
                }
            if isinstance(decoded, Mapping):
                response = dict(decoded)
                if response.get("id") is None:
                    response["id"] = rpc_id
                error = response.get("error")
                if isinstance(error, dict):
                    data = error.get("data")
                    detail = data.get("detail") if isinstance(data, Mapping) else None
                    if detail == "No runtime operation matched request.":
                        error["code"] = -32601
                        error["message"] = "Method not found"
                responses.append(response)
                continue
            responses.append(
                {"jsonrpc": "2.0", "result": decoded, "id": rpc_id}
            )

        return responses

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        temp = getattr(ctx, "temp", None)
        dispatch = temp.get("dispatch") if isinstance(temp, dict) else None
        rpc_batch = dispatch.get("rpc_batch") if isinstance(dispatch, dict) else None
        if isinstance(rpc_batch, list):
            egress = temp.setdefault("egress", {}) if isinstance(temp, dict) else {}
            if isinstance(egress, dict):
                egress["transport_response"] = {
                    "status_code": 200,
                    "body": await self._execute_rpc_batch(ctx, rpc_batch),
                }
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
