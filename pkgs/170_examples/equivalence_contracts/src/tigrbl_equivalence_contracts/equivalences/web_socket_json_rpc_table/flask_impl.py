"""Flask-Sock implementation for the WebSocketJsonRpcTable Widget surface."""

from __future__ import annotations

import json

from flask import Flask, jsonify
from flask_sock import Sock
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
app = Flask(__name__)
app.config["SOCK_SERVER_OPTIONS"] = {"subprotocols": ["jsonrpc"]}
sock = Sock(app)


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@sock.route("/widgetwebsocketjsonrpctable")
def widget_socket_jsonrpc(ws):
    """Handle one JSON-RPC envelope through Flask-Sock."""

    envelope = json.loads(ws.receive())
    result = {"message": f"widget:{envelope['params']['message']}"}
    ws.send(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": envelope["id"],
                "result": result,
            },
            separators=(",", ":"),
        )
    )
