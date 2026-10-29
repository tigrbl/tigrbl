from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Uuid
from sqlalchemy.orm import Session
import tigrbl_ops_oltp

from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String
from tigrbl_atoms.atoms.sys import _oltp_context
from tigrbl_atoms.atoms.wire import validate_in
from tigrbl_typing.status.exceptions import HTTPException
from tigrbl_core.schema.builder.helpers import (
    _spec_python_type,
    _input_selector_entries,
)


def test_selector_schema_uses_declared_type_and_storage_fallback():
    spec = SimpleNamespace(
        field=SimpleNamespace(py_type=None),
        storage=SimpleNamespace(type_=Uuid(as_uuid=True), primary_key=True),
    )
    assert _spec_python_type(spec) is UUID
    entry = _input_selector_entries({"id": spec}, "read")["id"]
    assert entry["py_type"] is UUID
    assert entry["in_enabled"] is False
    assert _input_selector_entries({"id": spec}, "create") == {}
    spec.field.py_type = str
    assert _spec_python_type(spec) is str


@pytest.mark.parametrize("annotation,value", [(UUID, str(uuid4())), (int, "42")])
def test_validated_selector_reaches_persistence(annotation, value):
    ctx = SimpleNamespace(
        path_params={"item_id": value},
        payload={"id": "conflicting-body-value"},
        temp={
            "schema_in": {
                "fields": ("id",),
                "by_field": {"id": {"py_type": annotation, "selector": True}},
                "required": (),
            },
            "in_values": {"id": "conflicting-body-value"},
        },
    )
    validate_in._run(None, ctx)
    assert _oltp_context.path_params(ctx)["item_id"] == annotation(value)
    assert _oltp_context.payload(ctx)["id"] == annotation(value)


def test_invalid_route_selector_is_rejected_before_persistence():
    ctx = SimpleNamespace(
        path_params={"item_id": "invalid"},
        temp={
            "schema_in": {
                "fields": ("id",),
                "by_field": {"id": {"py_type": UUID, "selector": True}},
                "required": (),
            },
            "in_values": {},
        },
    )
    with pytest.raises(HTTPException) as error:
        validate_in._run(None, ctx)
    assert error.value.status_code == 422
    assert ctx.temp["in_invalid"] is True


@pytest.mark.parametrize("bulk", [False, True])
def test_persistence_payload_uses_validated_values(bulk):
    value = uuid4()
    original = {"related_id": str(value), "control": "preserved"}
    inbound = {"related_id": str(value)}
    ctx = SimpleNamespace(
        payload=[original] if bulk else original,
        temp={
            "schema_in": {
                "fields": ("related_id",),
                "by_field": {"related_id": {"py_type": UUID}},
                "required": (),
            },
            "in_values": [inbound] if bulk else inbound,
        },
    )
    validate_in._run(None, ctx)
    result = _oltp_context.payload(ctx)
    assert result == (
        [{"related_id": value, "control": "preserved"}]
        if bulk
        else {"related_id": value, "control": "preserved"}
    )


def test_bulk_delete_selector_collection_materializes():
    value = uuid4()
    ctx = SimpleNamespace(
        payload={"ids": [str(value)]},
        temp={
            "schema_in": {
                "fields": ("ids",),
                "by_field": {"ids": {"py_type": list[UUID]}},
                "required": (),
            },
            "in_values": {"ids": [str(value)]},
        },
    )
    validate_in._run(None, ctx)
    assert _oltp_context.payload(ctx)["ids"] == [value]


@pytest.mark.asyncio
async def test_rest_selector_and_uuid_body_materialize_before_database(
    sync_db_session, monkeypatch
):
    engine, _ = sync_db_session

    def get_db():
        with Session(engine) as session:
            yield session
            session.commit()

    class MaterializedWidget(TableBase, GUIDPk):
        __tablename__ = "materialized_widgets"
        __resource__ = "materialized-widget"
        name = Column(String)
        related_id = Column(Uuid(as_uuid=True))

    app = TigrblApp(get_db=get_db)
    app.include_table(MaterializedWidget, prefix="")
    app.initialize()
    related = uuid4()
    update = tigrbl_ops_oltp.update
    seen = []

    async def observe_update(model, ident, data, db):
        assert isinstance(ident, UUID)
        assert isinstance(data["id"], UUID)
        result = await update(model, ident, data, db)
        # CRUD promises a flush, while transaction ownership stays with the caller.
        db.expire(result)
        assert result.name == "changed"
        seen.append(ident)
        return result

    monkeypatch.setattr(tigrbl_ops_oltp, "update", observe_update)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post(
            "/materialized-widget", json={"name": "first", "related_id": str(related)}
        )
        assert created.status_code == 201, created.text
        first = created.json()["id"]
        other = await client.post("/materialized-widget", json={"name": "second"})
        assert other.status_code == 201, other.text
        second = other.json()["id"]
        changed = await client.patch(
            f"/materialized-widget/{first}", json={"id": second, "name": "changed"}
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["id"] == first, changed.text
        assert changed.json()["name"] == "changed", changed.text
        assert seen == [UUID(first)]
        assert (await client.get(f"/materialized-widget/{second}")).json()[
            "name"
        ] == "second"
        invalid = await client.get("/materialized-widget/not-a-uuid")
        assert invalid.status_code == 422, invalid.text
    with Session(engine) as session:
        stored = session.get(MaterializedWidget, UUID(first))
        assert stored.related_id == related
