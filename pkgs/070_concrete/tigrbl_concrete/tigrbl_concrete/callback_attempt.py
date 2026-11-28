"""Opt-in SQL persistence for one outbound callback row per attempt."""

from __future__ import annotations

from contextlib import asynccontextmanager
from inspect import isawaitable
from time import time
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase
from ._mapping.model import _materialize_handlers
from tigrbl_core._spec.op_spec import resolve


class _CallbackStorageBase(DeclarativeBase):
    pass


class CallbackAttempt(_CallbackStorageBase):
    __tablename__ = "tigrbl_callback_attempt"
    __table_args__ = (UniqueConstraint("delivery_id", "attempt_number"),)

    id = Column(String(32), primary_key=True)
    delivery_id = Column(String(32), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    request = Column(JSON, nullable=True)
    identity = Column(JSON, nullable=False)
    status = Column(String(24), nullable=False, index=True)
    available_at = Column(Float, nullable=False)
    emit_expires_at = Column(Float)
    started_at = Column(Float)
    finished_at = Column(Float)
    claim = Column(String(32))
    claim_expires_at = Column(Float)
    keep_result = Column(Boolean, nullable=False)
    retry_exhausted = Column(Boolean, nullable=False, default=False)
    http_status = Column(Integer)
    response_body = Column(Text)
    error = Column(String(120))


async def _await(value):
    return await value if isawaitable(value) else value


@asynccontextmanager
async def _transaction(session_factory):
    db = session_factory()
    try:
        yield db
        await _await(db.commit())
    except BaseException:
        await _await(db.rollback())
        raise
    finally:
        await _await(db.close())


_materialize_handlers(CallbackAttempt, resolve(CallbackAttempt))


async def insert_attempt(db, row):
    return await CallbackAttempt.handlers.create.core(db=db, payload=row)


async def _update_attempt(db, attempt_id, values):
    return await CallbackAttempt.handlers.update.core(
        db=db, path_params={"id": attempt_id}, payload=values
    )


def _table():
    return CallbackAttempt.__table__


def next_attempt(row, *, available_at):
    return {
        "id": uuid4().hex,
        "delivery_id": row["delivery_id"],
        "attempt_number": row["attempt_number"] + 1,
        "request": row["request"],
        "identity": row["identity"],
        "status": "pending",
        "available_at": available_at,
        "keep_result": row["keep_result"],
    }


async def claim_attempt(session_factory, attempt_id=None):
    now = time()
    table = _table()
    eligible = (table.c.status == "pending") & (table.c.available_at <= now)
    statement = select(table).where(eligible).order_by(table.c.available_at, table.c.id)
    if attempt_id is not None:
        statement = statement.where(table.c.id == attempt_id)
    async with _transaction(session_factory) as db:
        row = (await _await(db.execute(statement.limit(1)))).mappings().first()
        if row is None:
            return None
        token = uuid4().hex
        changes = {
            "status": "started",
            "claim": token,
            "started_at": now,
            "claim_expires_at": now + row["request"]["timeout_seconds"] + 30,
        }
        result = await _await(
            db.execute(
                update(table).where(table.c.id == row["id"], eligible).values(**changes)
            )
        )
        return {**row, **changes} if result.rowcount == 1 else None


async def release_attempt(session_factory, attempt_id, emitted):
    table = _table()
    now = time()
    eligible = (table.c.id == attempt_id) & (table.c.status == "awaiting_emit")
    if emitted:
        eligible = eligible & (table.c.emit_expires_at > now)
    async with _transaction(session_factory) as db:
        result = await _await(
            db.execute(
                update(table)
                .where(eligible)
                .values(
                    status="pending" if emitted else "cancelled",
                    finished_at=None if emitted else now,
                )
            )
        )
        return result.rowcount == 1


async def finish_attempt(
    session_factory,
    row,
    outcome,
    *,
    retry=False,
    trace_identity=None,
    record_outcome=None,
    expired=False,
):
    """Fence a terminal write against the active claim and schedule retries atomically."""
    table = _table()
    now = time()
    values = {
        "status": outcome["status"],
        "finished_at": now,
        "claim": None,
        "claim_expires_at": None,
        "retry_exhausted": bool(outcome.get("retryable", retry))
        and row["attempt_number"] >= row["request"]["max_attempts"],
    }
    if row["keep_result"]:
        values.update(
            {
                name: outcome.get(name)
                for name in ("http_status", "response_body", "error")
            }
        )
    async with _transaction(session_factory) as db:
        if row.get("claim") is None:
            await insert_attempt(
                db,
                {
                    **row,
                    **values,
                    "request": None,
                    "started_at": row.get("started_at", now),
                },
            )
        else:
            # Compare and take the row lock before applying the model update.
            result = await _await(
                db.execute(
                    update(table)
                    .where(
                        table.c.id == row["id"],
                        table.c.status == "started",
                        table.c.claim == row["claim"],
                        table.c.claim_expires_at <= now
                        if expired
                        else table.c.claim_expires_at > now,
                    )
                    .values(claim=None)
                )
            )
            if result.rowcount != 1:
                return None
            await _update_attempt(db, row["id"], values)
        if record_outcome is not None:
            await _await(record_outcome(db=db, payload={**row, "outcome": outcome}))
        if trace_identity is not None:
            identity = getattr(db, "transaction_id", None)
            if identity is not None:
                trace_identity["transaction_id"] = identity
        if retry and row["attempt_number"] < row["request"]["max_attempts"]:
            following = next_attempt(
                row,
                available_at=now + row["request"]["retry_delay_seconds"],
            )
            await insert_attempt(db, following)
            return following
    return False


async def find_expired_attempts(session_factory, *, limit=100):
    table = _table()
    now = time()
    async with _transaction(session_factory) as db:
        await _await(
            db.execute(
                update(table)
                .where(
                    table.c.status == "awaiting_emit",
                    table.c.emit_expires_at <= now,
                )
                .values(status="cancelled", finished_at=now)
            )
        )
        result = await _await(
            db.execute(
                select(table)
                .where(
                    table.c.status == "started",
                    table.c.claim_expires_at <= now,
                )
                .limit(limit)
            )
        )
        return [dict(row) for row in result.mappings()]


__all__ = ["CallbackAttempt"]
