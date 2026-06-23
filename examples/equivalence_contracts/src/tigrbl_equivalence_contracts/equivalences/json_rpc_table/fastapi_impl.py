"""FastAPI implementation for the JsonRpcTable Widget route surface."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_json_rpc_table"
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


@app.get("/widgetjsonrpctable", response_model=list[WidgetOut])
def list_widgets() -> list[WidgetOut]:
    with Session(engine) as session:
        rows = session.query(WidgetRow).order_by(WidgetRow.id).all()
        return [WidgetOut(id=row.id, name=row.name) for row in rows]


@app.post("/widgetjsonrpctable", response_model=WidgetOut, status_code=201)
def create_widget(payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = WidgetRow(id=payload.id, name=payload.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.delete("/widgetjsonrpctable")
def clear_widgets() -> dict[str, int]:
    with Session(engine) as session:
        deleted = session.query(WidgetRow).delete()
        session.commit()
        return {"deleted": deleted}


@app.get("/widgetjsonrpctable/{item_id}", response_model=WidgetOut)
def read_widget(item_id: str) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise HTTPException(status_code=404)
        return WidgetOut(id=row.id, name=row.name)


@app.patch("/widgetjsonrpctable/{item_id}", response_model=WidgetOut)
def update_widget(item_id: str, payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise HTTPException(status_code=404)
        row.name = payload.name
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.put("/widgetjsonrpctable/{item_id}", response_model=WidgetOut)
def replace_widget(item_id: str, payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            row = WidgetRow(id=item_id, name=payload.name)
            session.add(row)
        else:
            row.name = payload.name
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.delete("/widgetjsonrpctable/{item_id}")
def delete_widget(item_id: str) -> dict[str, int]:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise HTTPException(status_code=404)
        session.delete(row)
        session.commit()
        return {"deleted": 1}
