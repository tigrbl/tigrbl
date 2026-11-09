import os
import time
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Mapped, Session

import tigrbl_ops_oltp as crud
from tigrbl import RestBulkCrudTable, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import UUID7Pk
from tigrbl.orm.tables import TableBase
from tigrbl.schema import _build_schema
from tigrbl.specs import S, acol
from tigrbl.types import String


RFC_UUID7 = UUID("017f22e2-79b0-7cc3-98c4-dc0c0c07398f")


@pytest.fixture
def widget(request):
    base = getattr(request, "param", TableBase)

    class Widget(base, UUID7Pk):
        __tablename__ = f"uuid7_widgets_{uuid4().hex}"
        __resource__ = "uuid7-widget"
        name: Mapped[str] = acol(storage=S(type_=String))

    return Widget


@pytest.fixture(params=["sqlite", "postgresql"])
def engine(request, widget):
    url = "sqlite://"
    if request.param == "postgresql":
        url = os.environ.get("TIGRBL_TEST_POSTGRES_DSN")
        if not url:
            pytest.skip("Set TIGRBL_TEST_POSTGRES_DSN for the live PostgreSQL case")
    db_engine = create_engine(url)
    widget.__table__.create(db_engine)
    try:
        yield db_engine
    finally:
        widget.__table__.drop(db_engine)
        db_engine.dispose()


@pytest.mark.asyncio
async def test_uuid7_orm_crud_and_bulk(widget, engine):
    with Session(engine) as db:
        before = time.time_ns() // 1_000_000
        created = await crud.create(widget, {"name": "created"}, db)
        key = created.id
        assert key.version == 7
        assert before <= key.int >> 80 <= time.time_ns() // 1_000_000
        first, second = await crud.bulk_create(
            widget, [{"id": RFC_UUID7, "name": "supplied"}, {"name": "generated"}], db
        )
        bulk_key = second.id
        assert first.id == RFC_UUID7
        assert bulk_key.version == 7
        assert len({key, RFC_UUID7, bulk_key}) == 3
        db.commit()

    with Session(engine) as db:
        if engine.dialect.name == "postgresql":
            sql = text(
                f'SELECT pg_typeof(id)::text FROM "{widget.__tablename__}" LIMIT 1'
            )
            assert db.scalar(sql) == "uuid"
        assert (await crud.read(widget, RFC_UUID7, db)).id.bytes == RFC_UUID7.bytes
        await crud.update(widget, key, {"name": "updated"}, db)
        await crud.bulk_update(widget, [{"id": RFC_UUID7, "name": "bulk updated"}], db)
        await crud.bulk_replace(widget, [{"id": bulk_key, "name": "bulk replaced"}], db)
        await crud.bulk_merge(widget, [{"id": bulk_key, "name": "bulk merged"}], db)
        db.commit()

    with Session(engine) as db:
        assert (await crud.read(widget, key, db)).name == "updated"
        assert (await crud.read(widget, RFC_UUID7, db)).name == "bulk updated"
        assert (await crud.read(widget, bulk_key, db)).name == "bulk merged"
        await crud.delete(widget, key, db)
        assert await crud.bulk_delete(widget, [RFC_UUID7, bulk_key], db) == {
            "deleted": 2
        }
        db.commit()

    with Session(engine) as db:
        assert all(
            db.get(widget, ident) is None for ident in (key, RFC_UUID7, bulk_key)
        )
        db.add(widget(id=uuid4(), name="wrong version"))
        with pytest.raises(StatementError, match="UUID version 7"):
            db.flush()


def test_uuid7_selector_schema(widget):
    assert "id" not in _build_schema(widget, verb="create").model_fields
    schema = _build_schema(widget, verb="update")
    assert schema.model_validate({"id": str(RFC_UUID7)}).id == RFC_UUID7
    wrong_variant = UUID(int=RFC_UUID7.int ^ (1 << 63))
    for invalid in (uuid4(), wrong_variant, "malformed"):
        with pytest.raises(ValidationError):
            schema.model_validate({"id": invalid})


@pytest.mark.asyncio
async def test_uuid7_rest_atoms_and_patch_persistence(widget):
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(widget, prefix="")
    await app.initialize()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/uuid7-widget", json={"name": "before"})
        assert created.status_code == 201, created.text
        key = created.json()["id"]
        assert UUID(key).version == 7
        url = f"/uuid7-widget/{key}"
        wrong_version = await client.get(f"/uuid7-widget/{uuid4()}")
        assert wrong_version.status_code == 422, wrong_version.text
        changed = await client.patch(url, json={"id": str(RFC_UUID7), "name": "after"})
        assert changed.status_code == 200, changed.text
        assert changed.json() == {"id": key, "name": "after"}
        reloaded = await client.get(url)
        assert reloaded.json() == changed.json()
        deleted = await client.delete(url)
        assert deleted.json() == {"deleted": 1}
        assert (await client.get(url)).status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("widget", [RestBulkCrudTable], indirect=True)
async def test_uuid7_bulk_rest_atoms(widget):
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(widget, prefix="")
    await app.initialize()
    url = "/uuid7-widget"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post(url, json=[{"name": "first"}, {"name": "second"}])
        assert created.status_code in {200, 201}, created.text
        first, second = (row["id"] for row in created.json())
        assert all(UUID(key).version == 7 for key in (first, second))

        rejected = await client.patch(
            url, json=[{"id": first, "name": "rejected"}, {"id": str(uuid4())}]
        )
        assert rejected.status_code == 422, rejected.text
        assert (await client.get(f"{url}/{first}")).json()["name"] == "first"

        updated = await client.patch(url, json=[{"id": first, "name": "updated"}])
        assert updated.status_code == 200, updated.text
        assert (await client.get(f"{url}/{first}")).json()["name"] == "updated"

        rejected = await client.request(
            "DELETE", url, json={"ids": [first, str(uuid4())]}
        )
        assert rejected.status_code == 422, rejected.text
        deleted = await client.request("DELETE", url, json={"ids": [first, second]})
        assert deleted.json() == {"deleted": 2}
        assert (await client.get(f"{url}/{first}")).status_code == 404
