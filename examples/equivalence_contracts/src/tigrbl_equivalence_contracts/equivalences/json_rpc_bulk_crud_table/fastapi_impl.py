"""FastAPI implementation for the JsonRpcBulkCrudTable Widget JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_json_rpc_bulk_crud_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
Base.metadata.create_all(engine)
app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/rpc")
async def jsonrpc(request: Request) -> dict[str, Any]:
    envelope = await request.json()
    method = envelope.get("method")
    params = envelope.get("params") or []
    request_id = envelope.get("id")
    try:
        result = _dispatch_jsonrpc(method, params)
        return {"jsonrpc": "2.0", "result": result, "id": request_id}
    except KeyError as exc:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"unknown method: {exc.args[0]}"},
            "id": request_id,
        }


def _dispatch_jsonrpc(method: str, params: Any) -> Any:
    if method == "WidgetJsonRpcBulkCrudTable.bulk_create":
        return _bulk_create(params)
    if method == "WidgetJsonRpcBulkCrudTable.bulk_update":
        return _bulk_update(params)
    if method == "WidgetJsonRpcBulkCrudTable.bulk_replace":
        return _bulk_replace(params)
    if method == "WidgetJsonRpcBulkCrudTable.bulk_delete":
        return _bulk_delete(params)
    if method == "WidgetJsonRpcBulkCrudTable.list":
        return _list_widgets()
    raise KeyError(method)


def _list_widgets() -> list[dict[str, str]]:
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return [{"id": row.id, "name": row.name} for row in rows]


def _bulk_create(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    with Session(engine) as session:
        for item in rows:
            session.add(WidgetRow(id=item["id"], name=item["name"]))
        session.commit()
    return _list_widgets()


def _bulk_update(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    updated: list[dict[str, str]] = []
    with Session(engine) as session:
        for item in rows:
            row = session.get(WidgetRow, item["id"])
            if row is None:
                continue
            row.name = item["name"]
            updated.append({"id": row.id, "name": row.name})
        session.commit()
    return sorted(updated, key=lambda row: row["id"])


def _bulk_replace(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    replaced: list[dict[str, str]] = []
    with Session(engine) as session:
        for item in rows:
            row = session.get(WidgetRow, item["id"])
            if row is None:
                row = WidgetRow(id=item["id"], name=item["name"])
                session.add(row)
            else:
                row.name = item["name"]
            replaced.append({"id": row.id, "name": row.name})
        session.commit()
    return sorted(replaced, key=lambda row: row["id"])


def _bulk_delete(ids: list[str]) -> dict[str, int]:
    deleted = 0
    with Session(engine) as session:
        for item_id in ids:
            row = session.get(WidgetRow, item_id)
            if row is None:
                continue
            session.delete(row)
            deleted += 1
        session.commit()
    return {"deleted": deleted}
