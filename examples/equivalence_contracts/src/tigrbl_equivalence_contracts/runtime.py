from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

from httpx import ASGITransport, AsyncClient


def call_asgi_get(app: Any, path: str) -> dict[str, Any]:
    async def _call() -> dict[str, Any]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(path)
        return {"status_code": response.status_code, "json": response.json()}

    return asyncio.run(_call())


def call_flask_get(app: Any, path: str) -> dict[str, Any]:
    with app.test_client() as client:
        response = client.get(path)
    return {"status_code": response.status_code, "json": response.get_json()}


def normalize_http_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status_code": int(result["status_code"]),
        "json": _freeze(result["json"]),
    }


def normalize_projection(result: Mapping[str, Any]) -> dict[str, Any]:
    return _freeze(result)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _freeze(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value
