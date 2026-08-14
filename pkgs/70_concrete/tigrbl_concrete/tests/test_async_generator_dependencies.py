from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_concrete._concrete._route import (
    ROUTE_OPS_MODEL_NAME,
    _invoke_route_handler,
    add_route,
)
from tigrbl_concrete._concrete.dependencies import Depends


@pytest.mark.asyncio
async def test_route_dependency_unwraps_and_closes_async_generator() -> None:
    events: list[str] = []

    async def database_session():
        events.append("opened")
        try:
            yield "database-session"
        finally:
            events.append("closed")

    async def handler(db=Depends(database_session)):
        events.append(f"handled:{db}")
        return {"db": db}

    owner = SimpleNamespace(
        routes=[],
        tables={},
        tags=None,
        prefix="",
        dependency_overrides={},
    )
    route = add_route(owner, "/probe", handler, methods=("GET",), name="probe")
    ctx = SimpleNamespace(
        app=owner,
        router=None,
        model=owner.tables[ROUTE_OPS_MODEL_NAME],
        op="probe",
        path_params={},
        temp={},
    )

    await _invoke_route_handler(route, ctx)

    assert ctx.result == {"db": "database-session"}
    assert events == ["opened", "handled:database-session", "closed"]
