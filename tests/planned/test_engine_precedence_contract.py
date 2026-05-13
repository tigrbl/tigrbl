from tigrbl_core._spec.app_spec import AppSpec, resolve_engine_name
from tigrbl_core._spec.engine_spec import EngineSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.table_spec import TableSpec


def test_engine_precedence_contract() -> None:
    app = AppSpec(
        engines=(
            EngineSpec(kind="sqlite", memory=True, name="app"),
            EngineSpec(kind="sqlite", memory=True, name="table"),
            EngineSpec(kind="sqlite", memory=True, name="op"),
        ),
        engine_name="app",
    )
    table = TableSpec(name="items", engine_name="table")
    op = OpSpec(alias="read", target="read", engine_name="op")

    assert resolve_engine_name(app, table=table, op=op) == "op"
    assert resolve_engine_name(app, table=table) == "table"
    assert resolve_engine_name(app) == "app"
