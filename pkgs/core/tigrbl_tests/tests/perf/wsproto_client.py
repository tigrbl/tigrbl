from __future__ import annotations

import asyncio
from urllib.parse import urlsplit

from wsproto import WSConnection
from wsproto.connection import ConnectionType
from wsproto.events import (
    AcceptConnection,
    CloseConnection,
    RejectConnection,
    TextMessage,
    Request,
)


async def websocket_text_roundtrip(url: str, outbound_text: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"ws", "wss"}:
        raise ValueError(f"unsupported websocket scheme: {parsed.scheme!r}")
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    target = parsed.path or "/"
    if parsed.query:
        target = f"{target}?{parsed.query}"
    reader, writer = await asyncio.open_connection(host, port)
    connection = WSConnection(ConnectionType.CLIENT)
    host_header = host if parsed.port is None else f"{host}:{port}"
    writer.write(
        connection.send(
            Request(
                host=host_header,
                target=target,
            )
        )
    )
    await writer.drain()

    try:
        while True:
            data = await reader.read(65536)
            if not data:
                raise RuntimeError("websocket handshake closed before acceptance")
            connection.receive_data(data)
            accepted = False
            for event in connection.events():
                if isinstance(event, AcceptConnection):
                    accepted = True
                    break
                if isinstance(event, RejectConnection):
                    raise RuntimeError(
                        f"websocket handshake rejected with status {event.status_code}"
                    )
            if accepted:
                break

        writer.write(connection.send(TextMessage(outbound_text)))
        await writer.drain()

        parts: list[str] = []
        while True:
            data = await reader.read(65536)
            if not data:
                break
            connection.receive_data(data)
            for event in connection.events():
                if isinstance(event, TextMessage):
                    parts.append(event.data)
                    if event.message_finished:
                        writer.write(connection.send(CloseConnection(code=1000)))
                        await writer.drain()
                        return "".join(parts)
                if isinstance(event, CloseConnection):
                    if parts:
                        return "".join(parts)
                    raise RuntimeError(
                        f"websocket closed before response with code {event.code}"
                    )
        return "".join(parts)
    finally:
        writer.close()
        await writer.wait_closed()
