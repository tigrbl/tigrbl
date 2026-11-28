from __future__ import annotations

from typing import Any, Mapping

from tigrbl_core.config.constants import __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__
from tigrbl_typing.channel import OpChannel


def _normalize_path(path: str) -> str:
    return path.rstrip("/") or "/"


def _resolve_jsonrpc_endpoint(ctx: Any, channel: OpChannel) -> str | None:
    if channel.kind != "http" or str(channel.method or "").upper() != "POST":
        return None

    path = _normalize_path(channel.path)
    route = {}
    temp = ctx.get("temp")
    if isinstance(temp, dict):
        route = temp.setdefault("route", {})
    if isinstance(route, Mapping):
        endpoint = route.get("endpoint")
        if isinstance(endpoint, str) and endpoint:
            return endpoint

    for owner_key in ("router", "app"):
        owner = ctx.get(owner_key)
        mounts = getattr(owner, "_jsonrpc_endpoint_mounts", None)
        if isinstance(mounts, Mapping):
            endpoint = mounts.get(path) or mounts.get(channel.path)
            if isinstance(endpoint, str) and endpoint:
                return endpoint

    for endpoint, mapped_path in __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__.items():
        if path == _normalize_path(mapped_path):
            return endpoint
    return None


_NO_ERROR_DATA = object()


def _jsonrpc_error_payload(code: int, message: str, request_id: Any, *, data: Any = _NO_ERROR_DATA) -> dict[str, Any]:
    """Construct the existing compatibility error envelope without choosing policy."""
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not _NO_ERROR_DATA:
        error["data"] = data
    return {"jsonrpc": "2.0", "error": error, "id": request_id}
