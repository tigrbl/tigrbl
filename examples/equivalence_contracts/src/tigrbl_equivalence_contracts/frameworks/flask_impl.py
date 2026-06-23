from __future__ import annotations

import socket
import threading
import time

from flask import Flask, abort, jsonify, request
import httpx
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool
from werkzeug.serving import make_server


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets"

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


@app.post("/widget")
def create_widget():
    payload = request.get_json()
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return jsonify({"id": row.id, "name": row.name}), 201


@app.get("/widget")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])


@app.get("/widget/<id>")
def read_widget(id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            abort(404)
        return jsonify({"id": row.id, "name": row.name})


@app.patch("/widget/<id>")
def update_widget(id: str):
    payload = request.get_json()
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            abort(404)
        row.name = payload["name"]
        session.commit()
        return jsonify({"id": row.id, "name": row.name})


@app.delete("/widget/<id>")
def delete_widget(id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            abort(404)
        session.delete(row)
        session.commit()
        return jsonify({"deleted": 1})


def assert_rest_crud_e2e() -> tuple[dict, ...]:
    port = _free_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    _wait_for_server(base_url)

    try:
        with httpx.Client(base_url=base_url, timeout=10.0) as client:
            client.delete("/widget/widget-1")

            create = client.post(
                "/widget", json={"id": "widget-1", "name": "First"}
            )
            assert create.status_code == 201
            assert create.json() == {"id": "widget-1", "name": "First"}

            read = client.get("/widget/widget-1")
            assert read.status_code == 200
            assert read.json() == {"id": "widget-1", "name": "First"}

            list_created = client.get("/widget")
            assert list_created.status_code == 200
            assert list_created.json() == [{"id": "widget-1", "name": "First"}]

            update = client.patch(
                "/widget/widget-1", json={"id": "widget-1", "name": "Second"}
            )
            assert update.status_code == 200
            assert update.json() == {"id": "widget-1", "name": "Second"}

            delete = client.delete("/widget/widget-1")
            assert delete.status_code == 200
            assert delete.json() == {"deleted": 1}

            list_deleted = client.get("/widget")
            assert list_deleted.status_code == 200
            assert list_deleted.json() == []

        return (
            {"step": "create", "status_code": 201, "json": create.json()},
            {"step": "read_created", "status_code": 200, "json": read.json()},
            {
                "step": "list_created",
                "status_code": 200,
                "json": list_created.json(),
            },
            {"step": "update", "status_code": 200, "json": update.json()},
            {"step": "delete", "status_code": 200, "json": delete.json()},
            {
                "step": "list_deleted",
                "status_code": 200,
                "json": list_deleted.json(),
            },
        )
    finally:
        server.shutdown()
        thread.join(timeout=10)


def _wait_for_server(base_url: str) -> None:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            httpx.get(base_url, timeout=0.5)
            return
        except (httpx.ConnectError, httpx.ReadError, httpx.ConnectTimeout):
            time.sleep(0.05)
    raise RuntimeError(f"server did not start at {base_url}")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
