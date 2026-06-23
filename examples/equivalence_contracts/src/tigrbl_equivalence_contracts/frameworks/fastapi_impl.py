from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
Base.metadata.create_all(engine)


class WidgetIn(BaseModel):
    id: str
    name: str


class WidgetOut(BaseModel):
    id: str
    name: str


app = FastAPI()


@app.post("/widgets", response_model=WidgetOut)
def create_widget(payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = WidgetRow(id=payload.id, name=payload.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.get("/widgets", response_model=list[WidgetOut])
def list_widgets() -> list[WidgetOut]:
    with Session(engine) as session:
        return [
            WidgetOut(id=row.id, name=row.name)
            for row in session.query(WidgetRow).order_by(WidgetRow.id)
        ]


@app.get("/widgets/{id}", response_model=WidgetOut)
def read_widget(id: str) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            raise HTTPException(status_code=404)
        return WidgetOut(id=row.id, name=row.name)


@app.patch("/widgets/{id}", response_model=WidgetOut)
def update_widget(id: str, payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            raise HTTPException(status_code=404)
        row.name = payload.name
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.delete("/widgets/{id}")
def delete_widget(id: str) -> dict[str, str]:
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            raise HTTPException(status_code=404)
        session.delete(row)
        session.commit()
        return {"deleted": id}


rest_crud_contract = {
    "resource": "Widget",
    "table": "widgets",
    "fields": {"id": "string", "name": "string"},
    "routes": (
        ("POST", "/widgets"),
        ("GET", "/widgets"),
        ("GET", "/widgets/{id}"),
        ("PATCH", "/widgets/{id}"),
        ("DELETE", "/widgets/{id}"),
    ),
}
