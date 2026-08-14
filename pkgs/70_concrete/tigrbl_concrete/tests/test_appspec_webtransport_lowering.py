from __future__ import annotations

from sqlalchemy import Column, String
from tigrbl_base._base import TableBase
from tigrbl_concrete._concrete import TigrblApp
from tigrbl_core._spec import (
    AppSpec,
    JsonRpcFramingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
    WebTransportBindingSpec,
)


class RoomSession(TableBase):
    __tablename__ = "webtransport_lowering_sessions"
    __allow_unmapped__ = True
    id = Column(String, primary_key=True)


def test_webtransport_path_lowering_materializes_owned_operation() -> None:
    binding = WebTransportBindingSpec(
        path="/r/{room_id_hash}",
        profile="bidi_stream",
        inner_framing=JsonRpcFramingSpec(),
        rpc_method="Session.hello",
    )
    table = TableSpec(
        name="RoomSession",
        resource="session",
        model_ref=f"{__name__}:RoomSession",
        ops=(
            OpSpec(
                alias="session_hello",
                target="custom",
                bindings=(binding,),
                persist="skip",
            ),
        ),
    )
    app = TigrblApp.from_spec(
        AppSpec(
            title="WebTransport lowering",
            routers=(
                RouterSpec(
                    name="realtime",
                    paths=(
                        PathSpec(
                            path="/r/{room_id_hash}",
                            kind="webtransport",
                            tables=(table,),
                        ),
                    ),
                ),
            ),
        )
    )

    assert app.tables["RoomSession"] is RoomSession
    plan = app.runtime.kernel.kernel_plan(app)
    rows = plan.proto_indices["webtransport"]["templated"]
    row = next(item for item in rows if item.get("rpc_method") == "Session.hello")

    assert row["path"] == "/r/{room_id_hash}"
    assert row["names"] == ("room_id_hash",)
    assert row["lane"] == "bidi_stream"
    assert plan.opmeta[row["meta_index"]].alias == "session_hello"