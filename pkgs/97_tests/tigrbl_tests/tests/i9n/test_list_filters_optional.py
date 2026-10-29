import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_list_filters_optional(app_client):
    client, _, _ = app_client
    spec = (await client.get("/openapi.json")).json()
    params = spec["paths"]["/tenant"]["get"].get("parameters", [])
    name_param = next(p for p in params if p["name"] == "name")
    assert name_param["required"] is False

    r = await client.get("/tenant")
    assert r.status_code == 200
    assert r.json() == []

    r2 = await client.get("/tenant", params={"name": "foo"})
    assert r2.status_code == 200
    assert r2.json() == []


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_list_filters_committed_rows(app_client):
    from tigrbl import resolver

    client, app, _ = app_client
    # Seed committed rows directly: this test exercises list predicates, not
    # transaction ownership of the create operation.
    tenant = app.tables["Tenant"]
    _, maker = resolver.resolve_provider(
        router=app, model=tenant, op_alias="list"
    ).ensure()
    session = maker()
    if hasattr(session, "__aenter__"):
        async with session:
            session.add_all([tenant(name="foo"), tenant(name="bar")])
            await session.commit()
    else:
        with session:
            session.add_all([tenant(name="foo"), tenant(name="bar")])
            session.commit()
    filtered = await client.get("/tenant", params={"name": "foo"})
    assert filtered.status_code == 200
    assert [row["name"] for row in filtered.json()] == ["foo"]
    core_filtered = await app.core.Tenant.list({"name": "foo"})
    assert [row["name"] for row in core_filtered] == ["foo"]
