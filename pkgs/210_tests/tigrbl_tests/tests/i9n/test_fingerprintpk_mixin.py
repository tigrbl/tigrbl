import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, insert, text
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Mapped, Session

from tigrbl import RestBulkCrudTable, TableBase, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import CRUD_IO, FingerprintPk
from tigrbl.schema import _build_schema
from tigrbl.specs import S, acol
from tigrbl.types import String


@pytest.fixture
def device_model(request):
    base = getattr(request, "param", TableBase)

    class Device(base, FingerprintPk):
        __tablename__ = f"fingerprint_devices_{base.__name__.lower()}"
        __resource__ = "fingerprint-device"
        name: Mapped[str] = acol(storage=S(type_=String, nullable=False), io=CRUD_IO)

    return Device


LOWERCASE = "7c:db:98:04:14:f5"
UPPERCASE = LOWERCASE.upper()


def test_fingerprint_primary_key_normalizes_orm_and_core_binds(device_model):
    with create_engine("sqlite://").begin() as connection:
        table = device_model.__table__
        table.create(connection)
        with Session(connection) as session:
            device = device_model(id=UPPERCASE, name="first")
            session.add(device)
            session.flush()
            assert device.id == LOWERCASE
            assert session.get(device_model, UPPERCASE) is device
            assert session.get(device_model, LOWERCASE) is device
            stored = connection.execute(text(f"SELECT id FROM {table.name}"))
            assert stored.scalar_one() == LOWERCASE

            with pytest.raises(ValueError, match="hexadecimal byte pairs"):
                device_model(id="invalid", name="invalid")
            with pytest.raises(IntegrityError), session.begin_nested():
                session.execute(insert(table).values(id=UPPERCASE, name="duplicate"))
            with pytest.raises(StatementError, match="hexadecimal byte pairs"):
                session.get(device_model, "invalid")


@pytest.mark.asyncio
async def test_fingerprint_primary_key_rest(device_model):
    id_schema = _build_schema(device_model, verb="create").model_json_schema()[
        "properties"
    ]["id"]
    assert id_schema["minLength"] == id_schema["maxLength"] == 17
    assert id_schema["pattern"] == r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(device_model, prefix="")
    await app.initialize()

    collection = "/fingerprint-device"
    member = f"{collection}/{UPPERCASE}"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for invalid in (
            None,
            "7c-db-98-04-14-f5",
            "7c:db:98:04:14:fg",
            f"{LOWERCASE}\n",
        ):
            response = await client.post(
                collection, json={"id": invalid, "name": "bad"}
            )
            assert response.status_code == 422, response.text
        assert (
            await client.post(collection, json={"name": "missing"})
        ).status_code == 422
        assert (await client.get(f"{collection}/invalid")).status_code == 422

        created = await client.post(
            collection, json={"id": UPPERCASE, "name": "before"}
        )
        assert created.status_code == 201, created.text
        assert created.json()["id"] == LOWERCASE
        assert (await client.get(member)).json() == created.json()

        updated = await client.patch(member, json={"name": "after"})
        assert updated.status_code == 200, updated.text
        assert updated.json() == {"id": LOWERCASE, "name": "after"}
        assert (await client.delete(member)).status_code == 200
        assert (await client.get(f"{collection}/{LOWERCASE}")).status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("device_model", [RestBulkCrudTable], indirect=True)
async def test_fingerprint_primary_key_bulk_rest(device_model):
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(device_model, prefix="")
    await app.initialize()

    collection = "/fingerprint-device"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post(
            collection, json=[{"id": UPPERCASE, "name": "before"}]
        )
        assert created.status_code == 201, created.text
        assert created.json() == [{"id": LOWERCASE, "name": "before"}]
        updated = await client.patch(
            collection, json=[{"id": UPPERCASE, "name": "after"}]
        )
        assert updated.status_code == 200, updated.text
        assert updated.json() == [{"id": LOWERCASE, "name": "after"}]
        deleted = await client.request("DELETE", collection, json={"ids": [UPPERCASE]})
        assert deleted.json() == {"deleted": 1}
