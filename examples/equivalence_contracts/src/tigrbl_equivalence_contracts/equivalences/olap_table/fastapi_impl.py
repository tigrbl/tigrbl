"""FastAPI implementation for the OlapTable Widget route surface."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_olap_table"
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


@app.get("/widgetolaptable", response_model=list[WidgetOut])
def list_widgets() -> list[WidgetOut]:
    with Session(engine) as session:
        rows = session.query(WidgetRow).order_by(WidgetRow.id).all()
        return [WidgetOut(id=row.id, name=row.name) for row in rows]


@app.post("/widgetolaptable", response_model=WidgetOut, status_code=201)
def create_widget(payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = WidgetRow(id=payload.id, name=payload.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.get("/widgetolaptable/{item_id}", response_model=WidgetOut)
def read_widget(item_id: str) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise HTTPException(status_code=404)
        return WidgetOut(id=row.id, name=row.name)
