"""FastAPI implementation for the WebSocketTable Widget WebSocket surface."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_web_socket_table"
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


@app.websocket("/widgetwebsockettable")
async def widget_socket(websocket: WebSocket) -> None:
    """Echo one Widget message through FastAPI's native WebSocket route."""

    await websocket.accept()
    message = await websocket.receive_text()
    await websocket.send_text(f"widget:{message}")
    await websocket.close()
