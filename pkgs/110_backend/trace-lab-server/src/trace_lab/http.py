"""HTTP responses and timestamps shared by the collector and demo."""

import json
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def reply(send, status, payload, content_type="application/json", *, headers=()):
    if content_type == "application/json":
        payload = json.dumps(payload, separators=(",", ":")).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", content_type.encode()),
                (b"cache-control", b"no-store"),
                (b"x-content-type-options", b"nosniff"),
                *headers,
            ],
        }
    )
    await send({"type": "http.response.body", "body": payload})
