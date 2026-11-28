from httpx import ASGITransport, Client

from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import F, IO, S
from tigrbl.factories import acol
from tigrbl.types import Mapped, String


class Widget(TableBase, GUIDPk):
    __tablename__ = "widgets_openapi_openrpc_separation"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


def _build_app() -> TigrblApp:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app


def test_openapi_schema_excludes_openrpc_endpoint() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    assert "/openrpc.json" not in payload["paths"]


def test_openrpc_schema_excludes_openapi_endpoint() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    method_names = {method["name"].lower() for method in payload["methods"]}
    assert all("openapi" not in name for name in method_names)
    assert all("openrpc" not in name for name in method_names)


def test_openapi_schema_excludes_openrpc_even_if_route_is_schema_visible() -> None:
    app = _build_app()

    def openrpc_override(_request):
        return {"openrpc": "1.2.6"}

    router = TigrblRouter()
    router.add_route(
        "/openrpc.json",
        openrpc_override,
        methods=["GET"],
        name="openrpc_json",
        include_in_schema=True,
    )
    app.include_router(router)

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    assert "/openrpc.json" not in payload["paths"]


def _openapi_result_schema(payload: dict, operation_id: str) -> dict:
    for path_item in payload["paths"].values():
        for operation in path_item.values():
            if operation.get("operationId") != operation_id:
                continue
            response = operation["responses"]["200"]
            return response["content"]["application/json"]["schema"]
    raise AssertionError(f"OpenAPI operation {operation_id!r} was not found")


def _openrpc_result_schema(payload: dict, method_name: str) -> dict:
    method = next(
        method for method in payload["methods"] if method["name"] == method_name
    )
    return method["result"]["schema"]


def test_openapi_and_openrpc_publish_equivalent_list_result_shapes() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        openapi_payload = client.get("/openapi.json").json()
        openrpc_payload = client.get("/openrpc.json").json()

    operation_id = next(
        operation["operationId"]
        for path_item in openapi_payload["paths"].values()
        for operation in path_item.values()
        if operation.get("operationId", "").endswith(".list")
    )
    openapi_schema = _openapi_result_schema(openapi_payload, operation_id)
    openrpc_schema = _openrpc_result_schema(openrpc_payload, f"{Widget.__name__}.list")

    assert openapi_schema["type"] == openrpc_schema["type"] == "array"
    assert openapi_schema["items"] == openrpc_schema["items"]
    item_ref = openapi_schema["items"]["$ref"].rsplit("/", maxsplit=1)[-1]
    assert (
        openapi_payload["components"]["schemas"][item_ref]
        == openrpc_payload["components"]["schemas"][item_ref]
    )
