import asyncio
from time import time

import pytest
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker

from tigrbl import CallbackSpec
from tigrbl_concrete.callback_attempt import (
    CallbackAttempt,
    claim_attempt,
    finish_attempt,
)
from tigrbl_concrete.callbacks import lower_callback, run_callback_attempts


@pytest.mark.asyncio
async def test_callback_stale_claim_cannot_replace_recovered_outcome(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'recovery.db'}")
    CallbackAttempt.__table__.create(engine)
    sessions = sessionmaker(engine)
    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {},
        delivery="worker",
        durability="attempts_and_results",
        session_factory=sessions,
        max_attempts=2,
        retry_delay_seconds=0,
    )
    with sessions.begin() as db:
        await lower_callback(spec, object, "PRE_COMMIT")({"db": db, "temp": {}})

    def claim():
        return asyncio.run(claim_attempt(sessions))

    candidates = await asyncio.gather(
        asyncio.to_thread(claim), asyncio.to_thread(claim)
    )
    assert sum(row is not None for row in candidates) == 1
    original = next(row for row in candidates if row is not None)
    with sessions.begin() as db:
        db.execute(update(CallbackAttempt).values(claim_expires_at=time() - 1))

    async def reject(endpoint, body, headers, timeout):
        assert headers["Idempotency-Key"] == original["delivery_id"]
        return {"status_code": 503}

    assert await run_callback_attempts(sessions, send=reject) == 1
    assert await finish_attempt(sessions, original, {"status": "delivered"}) is None
    with sessions() as db:
        attempts = list(
            db.scalars(select(CallbackAttempt).order_by(CallbackAttempt.attempt_number))
        )
        assert [row.attempt_number for row in attempts] == [1, 2]
        assert [row.status for row in attempts] == ["unknown", "failed"]
        assert not attempts[0].retry_exhausted
        assert attempts[1].retry_exhausted
        assert attempts[0].id != attempts[1].id
        assert attempts[0].delivery_id == attempts[1].delivery_id
    engine.dispose()


@pytest.mark.asyncio
async def test_expired_response_fence_cancels_attempt_without_sending(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fence.db'}")
    CallbackAttempt.__table__.create(engine)
    sessions = sessionmaker(engine)
    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {},
        delivery="after_emit",
        durability="attempts_and_results",
        session_factory=sessions,
    )
    with sessions.begin() as db:
        await lower_callback(spec, object, "PRE_COMMIT")({"db": db, "temp": {}})
        db.execute(update(CallbackAttempt).values(emit_expires_at=time() - 1))
    assert await run_callback_attempts(sessions) == 0
    with sessions() as db:
        assert db.scalar(select(CallbackAttempt.status)) == "cancelled"
    engine.dispose()
