from __future__ import annotations

import socket
import threading
import time

from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool
import uvicorn


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


class WidgetIn(BaseModel):
    id: str
    name: str


class WidgetOut(BaseModel):
    id: str
    name: str


app = FastAPI()


@app.post("/widget", response_model=WidgetOut, status_code=201)
def create_widget(payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = WidgetRow(id=payload.id, name=payload.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.get("/widget", response_model=list[WidgetOut])
def list_widgets() -> list[WidgetOut]:
    with Session(engine) as session:
        return [
            WidgetOut(id=row.id, name=row.name)
            for row in session.query(WidgetRow).order_by(WidgetRow.id)
        ]


@app.get("/widget/{id}", response_model=WidgetOut)
def read_widget(id: str) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            raise HTTPException(status_code=404)
        return WidgetOut(id=row.id, name=row.name)


@app.patch("/widget/{id}", response_model=WidgetOut)
def update_widget(id: str, payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            raise HTTPException(status_code=404)
        row.name = payload.name
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.delete("/widget/{id}")
def delete_widget(id: str) -> dict[str, int]:
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            raise HTTPException(status_code=404)
        session.delete(row)
        session.commit()
        return {"deleted": 1}


def assert_rest_crud_e2e() -> tuple[dict, ...]:
    port = _free_port()
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            lifespan="off",
            log_level="warning",
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
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
        server.should_exit = True
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
