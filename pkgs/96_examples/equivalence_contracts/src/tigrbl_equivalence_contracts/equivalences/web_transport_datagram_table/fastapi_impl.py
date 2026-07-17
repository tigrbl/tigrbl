"""FastAPI implementation for the WebTransportDatagramTable Widget route surface."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_web_transport_datagram_table"
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


@app.post("/widgetwebtransportdatagramtable", response_model=WidgetOut, status_code=201)
def create_widget(payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = WidgetRow(id=payload.id, name=payload.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)
