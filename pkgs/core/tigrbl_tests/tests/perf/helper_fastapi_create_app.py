from __future__ import annotations

import inspect
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class FastApiBenchmarkItem(Base):
    __tablename__ = "benchmark_fastapi_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class FastApiCreateIn(BaseModel):
    name: str


class FastApiCreateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


def create_fastapi_app(db_path: Path) -> FastAPI:
    """Build a FastAPI app using SQLAlchemy and Pydantic with one create command."""
    engine = create_engine(f"sqlite+pysqlite:///{db_path}", future=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        Base.metadata.create_all(engine)
        yield

    app = FastAPI(lifespan=lifespan)
    app.state.benchmark_engine = engine

    def get_session() -> Session:
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    @app.post("/items", response_model=FastApiCreateOut, status_code=201)
    def create_item(
        payload: FastApiCreateIn, session: Session = Depends(get_session)
    ) -> FastApiCreateOut:
        item = FastApiBenchmarkItem(name=payload.name)
        session.add(item)
        session.commit()
        session.refresh(item)
        return FastApiCreateOut.model_validate(item)

    return app


async def dispose_fastapi_app(app: FastAPI) -> None:
    raw_engine = getattr(getattr(app, "state", None), "benchmark_engine", None)
    dispose = getattr(raw_engine, "dispose", None)
    if not callable(dispose):
        return
    result: Any = dispose()
    if inspect.isawaitable(result):
        await result


def fetch_fastapi_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM benchmark_fastapi_item ORDER BY id"
        ).fetchall()
    return [row[0] for row in rows]


def fastapi_create_path() -> str:
    return "/items"
