from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp
from tigrbl import resolver as _resolver
from tigrbl._spec import F, IO, S
from tigrbl.factories.column import acol as spec_acol
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import BulkCapable, Mergeable, Replaceable
from tigrbl.orm.tables import TableBase
from tigrbl.types import String


WRITE_VERBS = (
    "create",
    "update",
    "replace",
    "merge",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
)
OUT_VERBS = (
    "read",
    "list",
    "merge",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
)


@dataclass(frozen=True)
class RowVerbCase:
    alias: str
    rest_method: str
    rest_path: str
    rest_body: Any
    rpc_params: Any
    mixins: tuple[type, ...] = ()
    seed_pair: bool = True


ROW_VERB_CASES = (
    RowVerbCase(
        alias="create",
        rest_method="POST",
        rest_path="/widget",
        rest_body={"id": "rest-create", "name": "created"},
        rpc_params={"id": "rpc-create", "name": "created"},
        seed_pair=False,
    ),
    RowVerbCase(
        alias="read",
        rest_method="GET",
        rest_path="/widget/rest-read",
        rest_body=None,
        rpc_params={"id": "rpc-read"},
    ),
    RowVerbCase(
        alias="update",
        rest_method="PATCH",
        rest_path="/widget/rest-update",
        rest_body={"name": "updated"},
        rpc_params={"id": "rpc-update", "name": "updated"},
    ),
    RowVerbCase(
        alias="replace",
        rest_method="PUT",
        rest_path="/widget/rest-replace",
        rest_body={"id": "rest-replace", "name": "replaced"},
        rpc_params={"id": "rpc-replace", "name": "replaced"},
    ),
    RowVerbCase(
        alias="delete",
        rest_method="DELETE",
        rest_path="/widget/rest-delete",
        rest_body=None,
        rpc_params={"id": "rpc-delete"},
    ),
    RowVerbCase(
        alias="merge",
        rest_method="PATCH",
        rest_path="/widget/rest-merge",
        rest_body={"id": "rest-merge", "name": "merged"},
        rpc_params={"id": "rpc-merge", "name": "merged"},
        mixins=(Mergeable,),
    ),
)


def _build_app(suffix: str, *mixins: type) -> tuple[TigrblApp, type[TableBase]]:
    class_name = "Metamorphic" + "".join(
        part.title() for part in suffix.split("_")
    )
    io = IO(
        in_verbs=WRITE_VERBS,
        out_verbs=OUT_VERBS,
        mutable_verbs=WRITE_VERBS,
    )
    model = type(
        class_name,
        (TableBase, *mixins),
        {
            "__tablename__": f"metamorphic_{suffix}",
            "__allow_unmapped__": True,
            "__module__": __name__,
            "resource_name": "widget",
            "id": spec_acol(
                storage=S(type_=String(80), primary_key=True),
                field=F(py_type=str),
                io=io,
            ),
            "name": spec_acol(
                storage=S(type_=String(80), nullable=False),
                field=F(py_type=str),
                io=io,
            ),
        },
    )
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(model)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    return app, model


async def _rest(
    client: AsyncClient,
    method: str,
    path: str,
    *,
    json: Any = None,
    expected_status: tuple[int, ...] = (200,),
) -> Any:
    response = await client.request(method, path, json=json)
    assert response.status_code in expected_status, response.text
    if not response.content:
        return None
    return response.json()


async def _rpc(
    client: AsyncClient,
    model: type[TableBase],
    alias: str,
    params: Any,
    *,
    request_id: int = 1,
) -> Any:
    response = await client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": f"{model.__name__}.{alias}",
            "params": params,
            "id": request_id,
        },
    )
    assert response.status_code == 200, response.text
    envelope = response.json()
    assert envelope["jsonrpc"] == "2.0"
    assert envelope["id"] == request_id
    assert "error" not in envelope, envelope
    return envelope["result"]


async def _create_rows(client: AsyncClient, rows: list[dict[str, str]]) -> None:
    for row in rows:
        await _rest(
            client,
            "POST",
            "/widget",
            json=row,
            expected_status=(200, 201),
        )


async def _bulk_create_rows(client: AsyncClient, rows: list[dict[str, str]]) -> None:
    await _rest(
        client,
        "POST",
        "/widget",
        json=rows,
        expected_status=(200, 201),
    )


def _row_without_id(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key != "id"}


def _rows_without_ids(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted((_row_without_id(row) for row in rows), key=lambda row: row["name"])


def _rows_by_id(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: row["id"])


def _rows(prefix: str, alias: str, names: tuple[str, ...]) -> list[dict[str, str]]:
    return [
        {"id": f"{prefix}-{alias}-{index}", "name": name}
        for index, name in enumerate(names, start=1)
    ]


def _cleanup() -> None:
    _resolver.set_default(None)
    TableBase.metadata.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    ROW_VERB_CASES,
    ids=[case.alias for case in ROW_VERB_CASES],
)
async def test_rest_and_jsonrpc_row_default_verbs_are_metamorphic(
    case: RowVerbCase,
) -> None:
    TableBase.metadata.clear()
    app, model = _build_app(f"row_{case.alias}", *case.mixins)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            if case.seed_pair:
                await _create_rows(
                    client,
                    [
                        {
                            "id": f"rest-{case.alias}",
                            "name": f"{case.alias}-before",
                        },
                        {
                            "id": f"rpc-{case.alias}",
                            "name": f"{case.alias}-before",
                        },
                    ],
                )

            rest_result = await _rest(
                client,
                case.rest_method,
                case.rest_path,
                json=case.rest_body,
                expected_status=(200, 201),
            )
            rpc_result = await _rpc(client, model, case.alias, case.rpc_params)

        if case.alias == "delete":
            assert rest_result == rpc_result == {"deleted": 1}
        else:
            assert _row_without_id(rest_result) == _row_without_id(rpc_result)
    finally:
        _cleanup()


@pytest.mark.asyncio
async def test_rest_and_jsonrpc_list_default_verb_are_metamorphic() -> None:
    TableBase.metadata.clear()
    app, model = _build_app("list")
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            await _rest(
                client,
                "POST",
                "/widget",
                json={"id": "rest-list-1", "name": "rest-seeded"},
                expected_status=(200, 201),
            )
            await _rpc(
                client,
                model,
                "create",
                {"id": "rpc-list-1", "name": "rpc-seeded"},
            )

            rest_result = await _rest(client, "GET", "/widget")
            rpc_result = await _rpc(client, model, "list", {}, request_id=2)

        assert _rows_by_id(rest_result) == _rows_by_id(rpc_result)
    finally:
        _cleanup()


async def _clear_result(suffix: str, *, via_rpc: bool) -> tuple[dict[str, int], list]:
    TableBase.metadata.clear()
    app, model = _build_app(suffix)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            await _create_rows(
                client,
                [
                    {"id": f"{suffix}-1", "name": "first"},
                    {"id": f"{suffix}-2", "name": "second"},
                ],
            )
            if via_rpc:
                result = await _rpc(client, model, "clear", {"filters": {}})
            else:
                result = await _rest(
                    client,
                    "DELETE",
                    "/widget",
                    json={"filters": {}},
                )
            remaining = await _rest(client, "GET", "/widget")
        return result, remaining
    finally:
        _cleanup()


@pytest.mark.asyncio
async def test_rest_and_jsonrpc_clear_default_verb_are_metamorphic() -> None:
    rest_result, rest_remaining = await _clear_result("clear_rest", via_rpc=False)
    rpc_result, rpc_remaining = await _clear_result("clear_rpc", via_rpc=True)

    assert rest_result == rpc_result == {"deleted": 2}
    assert rest_remaining == rpc_remaining == []


@dataclass(frozen=True)
class BulkVerbCase:
    alias: str
    rest_method: str
    mixins: tuple[type, ...]
    seed_rows: tuple[dict[str, str], ...]
    rest_payload: Any
    rpc_params: Any
    seed_with_bulk_create: bool = True


BULK_VERB_CASES = (
    BulkVerbCase(
        alias="bulk_create",
        rest_method="POST",
        mixins=(BulkCapable,),
        seed_rows=(),
        rest_payload=_rows("rest", "bulk-create", ("first", "second")),
        rpc_params=_rows("rpc", "bulk-create", ("first", "second")),
    ),
    BulkVerbCase(
        alias="bulk_update",
        rest_method="PATCH",
        mixins=(BulkCapable,),
        seed_rows=tuple(
            _rows("rest", "bulk-update", ("old-first", "old-second"))
            + _rows("rpc", "bulk-update", ("old-first", "old-second"))
        ),
        rest_payload=_rows("rest", "bulk-update", ("new-first", "new-second")),
        rpc_params=_rows("rpc", "bulk-update", ("new-first", "new-second")),
    ),
    BulkVerbCase(
        alias="bulk_replace",
        rest_method="PUT",
        mixins=(BulkCapable, Replaceable),
        seed_rows=tuple(
            _rows("rest", "bulk-replace", ("old-first", "old-second"))
            + _rows("rpc", "bulk-replace", ("old-first", "old-second"))
        ),
        rest_payload=_rows("rest", "bulk-replace", ("new-first", "new-second")),
        rpc_params=_rows("rpc", "bulk-replace", ("new-first", "new-second")),
    ),
    BulkVerbCase(
        alias="bulk_merge",
        rest_method="PATCH",
        mixins=(Mergeable,),
        seed_rows=tuple(
            _rows("rest", "bulk-merge", ("old-first",))
            + _rows("rpc", "bulk-merge", ("old-first",))
        ),
        rest_payload=[
            {"id": "rest-bulk-merge-1", "name": "merged-first"},
            {"id": "rest-bulk-merge-2", "name": "merged-second"},
        ],
        rpc_params=[
            {"id": "rpc-bulk-merge-1", "name": "merged-first"},
            {"id": "rpc-bulk-merge-2", "name": "merged-second"},
        ],
        seed_with_bulk_create=False,
    ),
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    BULK_VERB_CASES,
    ids=[case.alias for case in BULK_VERB_CASES],
)
async def test_rest_and_jsonrpc_bulk_row_default_verbs_are_metamorphic(
    case: BulkVerbCase,
) -> None:
    TableBase.metadata.clear()
    app, model = _build_app(case.alias, *case.mixins)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            if case.seed_rows:
                if case.seed_with_bulk_create:
                    await _bulk_create_rows(client, list(case.seed_rows))
                else:
                    await _create_rows(client, list(case.seed_rows))

            rest_result = await _rest(
                client,
                case.rest_method,
                "/widget",
                json=case.rest_payload,
                expected_status=(200, 201),
            )
            rpc_result = await _rpc(client, model, case.alias, case.rpc_params)

        assert _rows_without_ids(rest_result) == _rows_without_ids(rpc_result)
    finally:
        _cleanup()


@pytest.mark.asyncio
async def test_rest_and_jsonrpc_bulk_delete_default_verb_are_metamorphic() -> None:
    TableBase.metadata.clear()
    app, model = _build_app("bulk_delete", BulkCapable)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            await _bulk_create_rows(
                client,
                _rows("rest", "bulk-delete", ("first", "second"))
                + _rows("rpc", "bulk-delete", ("first", "second")),
            )

            rest_result = await _rest(
                client,
                "DELETE",
                "/widget",
                json=["rest-bulk-delete-1", "rest-bulk-delete-2"],
            )
            rpc_result = await _rpc(
                client,
                model,
                "bulk_delete",
                ["rpc-bulk-delete-1", "rpc-bulk-delete-2"],
            )
            remaining = await _rest(client, "GET", "/widget")

        assert rest_result == rpc_result == {"deleted": 2}
        assert remaining == []
    finally:
        _cleanup()
