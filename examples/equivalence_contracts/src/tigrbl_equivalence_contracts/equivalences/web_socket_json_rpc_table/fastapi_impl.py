"""FastAPI implementation for the WebSocketJsonRpcTable Widget surface."""

from __future__ import annotations

import json

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_web_socket_json_rpc_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
Base.metadata.create_all(engine)


class WidgetIn(BaseModel):
    id: str
    name: str


class WidgetOut(BaseModel):
    id: str
    name: str


app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/widgetwebsocketjsonrpctable")
async def widget_socket_jsonrpc(websocket: WebSocket) -> None:
    """Handle one JSON-RPC envelope over FastAPI's native WebSocket route."""

    await websocket.accept(subprotocol="jsonrpc")
    envelope = json.loads(await websocket.receive_text())
    result = {"message": f"widget:{envelope['params']['message']}"}
    await websocket.send_text(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": envelope["id"],
                "result": result,
            },
            separators=(",", ":"),
        )
    )
    await websocket.close()
