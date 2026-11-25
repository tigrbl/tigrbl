import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from tigrbl import CallbackSpec
from tigrbl_concrete.callback_attempt import CallbackAttempt
from tigrbl_concrete.callbacks import lower_callback, run_callback_attempts


@pytest.fixture
def sessions(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'callbacks.db'}")
    CallbackAttempt.__table__.create(engine)
    yield sessionmaker(engine)
    engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "durability", ["none", "results", "attempts", "attempts_and_results"]
)
async def test_callback_durability_and_outcome_transaction(sessions, durability):
    observations = []

    async def send(*args):
        with sessions() as observer:
            observations.extend(observer.scalars(select(CallbackAttempt.status)))
        return {"status_code": 202, "body": "accepted"}

    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {"i": 1},
        durability=durability,
        session_factory=sessions,
        send=send,
    )
    ctx = {"temp": {}}
    durable_intent = durability in {"attempts", "attempts_and_results"}
    with sessions.begin() as db:
        ctx["db"] = db
        if durable_intent:
            await lower_callback(spec, object, "PRE_COMMIT")(ctx)
        with sessions() as observer:
            assert list(observer.scalars(select(CallbackAttempt.status))) == []
    # Outcome persistence cannot depend on the original session.
    ctx.pop("db")
    await lower_callback(spec, object, "POST_COMMIT")(ctx)
    assert ctx["callback_results"]["paid"]["status"] == "delivered"
    assert observations == (["started"] if durable_intent else [])
    with sessions() as observer:
        rows = list(observer.scalars(select(CallbackAttempt)))
        if durability == "none":
            assert rows == []
        else:
            assert len(rows) == 1
            assert rows[0].status == "delivered"
            assert rows[0].http_status == (
                202 if durability in {"results", "attempts_and_results"} else None
            )
            assert (rows[0].request is not None) is durable_intent


@pytest.mark.asyncio
async def test_worker_only_observes_committed_intent(sessions):
    sent = []

    async def send(endpoint, body, headers, timeout):
        sent.append(headers["Idempotency-Key"])
        return {"status_code": 200}

    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {},
        delivery="worker",
        durability="attempts_and_results",
        session_factory=sessions,
    )
    stage = lower_callback(spec, object, "PRE_COMMIT")
    with sessions() as db:
        await stage({"db": db, "temp": {}})
        db.rollback()
    assert await run_callback_attempts(sessions, send=send) == 0
    with sessions.begin() as db:
        await stage({"db": db, "temp": {}})
    assert await run_callback_attempts(sessions, send=send) == 1
    assert len(sent) == 1


@pytest.mark.asyncio
async def test_callback_outcome_can_update_an_app_owned_row_in_same_write(sessions):
    from sqlalchemy import Column, Integer, MetaData, String, Table

    metadata = MetaData()
    resources = Table(
        "resources",
        metadata,
        Column("id", String, primary_key=True),
        Column("callback_status", Integer),
    )
    with sessions.begin() as db:
        metadata.create_all(db.connection())
        db.execute(resources.insert().values(id="invoice-1"))

    original_db = None
    transaction_checks = []

    async def record_outcome(*, db, payload):
        transaction_checks.append(db is not original_db)
        outcome = payload["outcome"]
        db.execute(
            resources.update()
            .where(resources.c.id == "invoice-1")
            .values(
                callback_status=outcome["http_status"],
            )
        )

    async def send(*args):
        return {"status_code": 204}

    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {},
        durability="attempts_and_results",
        session_factory=sessions,
        record_outcome=record_outcome,
        send=send,
    )
    ctx = {"temp": {}}
    with sessions.begin() as db:
        original_db = db
        ctx["db"] = db
        await lower_callback(spec, object, "PRE_COMMIT")(ctx)
    await lower_callback(spec, object, "POST_COMMIT")(ctx)

    with sessions() as db:
        assert db.scalar(select(resources.c.callback_status)) == 204
        assert db.scalar(select(CallbackAttempt.http_status)) == 204
    assert transaction_checks == [True]
