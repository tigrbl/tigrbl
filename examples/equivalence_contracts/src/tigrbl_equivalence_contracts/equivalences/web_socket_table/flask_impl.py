"""Flask implementation for the WebSocketTable Widget WebSocket surface."""

from __future__ import annotations

from flask import Flask, jsonify
from flask_sock import Sock
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
app = Flask(__name__)
sock = Sock(app)


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@sock.route("/widgetwebsockettable")
def widget_socket(ws):
    """Echo one Widget message through Flask-Sock's WebSocket route."""

    message = ws.receive()
    ws.send(f"widget:{message}")
