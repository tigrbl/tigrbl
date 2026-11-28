from __future__ import annotations

from typing import Any

from ...types import Atom, Ctx, OperatedCtx
from ...stages import Operated

from ... import events as _ev
from .._temp import _ensure_temp
from ._db import _in_transaction, _resolve_db_handle

ANCHOR = _ev.SYS_TX_COMMIT


def record_transaction_participation(temp, db, identity=None) -> None:
    transaction_id = getattr(db, "transaction_id", None)
    if transaction_id is None:
        return
    invocation = identity or temp.get("identity") or {}
    link = {
        key: invocation[key]
        for key in ("invocation_id", "attempt_id", "rpc_item_index")
        if key in invocation
    }
    link.update(engine_session_id=db.engine_session_id, transaction_id=transaction_id)
    links = temp.setdefault("transaction_participation", [])
    if link not in links:
        links.append(link)


def record_transaction_events(temp, db) -> None:
    events = getattr(db, "transaction_events", None)
    if callable(events):
        relevant = {
            link["transaction_id"] for link in temp.get("transaction_participation", ())
        }
        temp["transaction_events"] = tuple(
            event for event in events() if event["transaction_id"] in relevant
        )
        flushes = getattr(db, "flush_events", None)
        if callable(flushes):
            temp["flush_events"] = tuple(
                event for event in flushes() if event.get("transaction_id") in relevant
            )


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    if temp.get("batch_resident_admitted") or temp.get("batch_resident_handled"):
        temp["__sys_tx_open__"] = False
        release = temp.pop("__sys_db_release__", None)
        if callable(release):
            rv = release()
            if hasattr(rv, "__await__"):
                await rv
        return
    db = _resolve_db_handle(ctx)
    open_flag = bool(temp.get("__sys_tx_open__")) or (
        db is not None and _in_transaction(db)
    )

    try:
        record_transaction_participation(temp, db)
        if not open_flag or db is None or temp.get("__sys_tx_joined__"):
            return
        commit = getattr(db, "commit", None)
        if callable(commit):
            rv = commit()
            if hasattr(rv, "__await__"):
                await rv
    finally:
        temp["__sys_tx_open__"] = False
        record_transaction_events(temp, db)
        release = temp.pop("__sys_db_release__", None)
        if callable(release):
            rv = release()
            if hasattr(rv, "__await__"):
                await rv


class AtomImpl(Atom[Operated, Operated, Exception]):
    name = "sys.commit_tx"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
