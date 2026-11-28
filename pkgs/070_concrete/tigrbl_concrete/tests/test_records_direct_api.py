from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_concrete.records import create_record, create_table_record


def test_direct_record_api_invokes_bound_table_operation() -> None:
    database = object()

    async def create(context: dict[str, object]) -> dict[str, object]:
        assert context["db"] is database
        assert context["target"] == "create"
        assert context["payload"] == {"email": "customer@bucketwarden.com"}
        return {"item": {"id": "customer-1"}}

    table = type(
        "Customer",
        (),
        {
            "handlers": SimpleNamespace(create=SimpleNamespace(core=create)),
            "ops": SimpleNamespace(
                by_alias={"create": SimpleNamespace(target="create")}
            ),
        },
    )

    result = asyncio.run(
        create_table_record(
            table,
            database,
            {"email": "customer@bucketwarden.com"},
        )
    )

    assert result == {"id": "customer-1"}
    assert create_record is create_table_record