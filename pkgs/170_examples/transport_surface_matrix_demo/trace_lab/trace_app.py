"""One loopback Tigrbl application with an identity-only event buffer."""

from pathlib import Path

from tigrbl import Column, TableBase, TigrblApp, Timeline
from tigrbl.factories.engine import sqlitef
from tigrbl_core._spec import (
    AppSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    JsonRpcFramingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from tigrbl_engine_sqlite.plugin import register as register_sqlite
from tigrbl_ops_realtime import InMemoryRealtimeBroker


WS_PATH = "/ws/activity"
WT_PATH = "/wt"


async def acknowledge(ctx):
    return {"accepted": True}


class Note(TableBase):
    __tablename__ = "trace_demo_notes"

    id = Column(
        storage=Column.S(primary_key=True, nullable=False),
        field=Column.F(py_type=str, required_in=("create",)),
        io=Column.IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    name = Column(
        storage=Column.S(nullable=False),
        field=Column.F(py_type=str, required_in=("create",)),
        io=Column.IO(in_verbs=("create",), out_verbs=("create", "read")),
    )

    __tigrbl_ops__ = (
        OpSpec(
            alias="create",
            target="create",
            tx_scope="read_write",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest", methods=("POST",), path="/notes"
                ),
            ),
        ),
        OpSpec(
            alias="Note.read",
            target="read",
            tx_scope="read_only",
            bindings=(
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc", rpc_method="Note.read", endpoint="/rpc"
                ),
            ),
        ),
        OpSpec(
            alias="echo",
            target="custom",
            arity="collection",
            tx_scope="none",
            handler=acknowledge,
            exchange="bidirectional_stream",
            bindings=(
                WebTransportBindingSpec(
                    proto="webtransport",
                    path=WT_PATH,
                    profile="bidi_stream",
                    inner_framing=JsonRpcFramingSpec(),
                    rpc_method="Trace.echo",
                ),
            ),
        ),
    )


class Activity(TableBase):
    __tablename__ = "trace_demo_activity"

    id = Column(
        storage=Column.S(primary_key=True, nullable=False),
        field=Column.F(py_type=str),
    )


def build_app(database: Path, timeline: Timeline):
    register_sqlite()
    binding = WsBindingSpec(
        proto="ws",
        path=WS_PATH,
        framing=JsonRpcFramingSpec(),
        subscription_ack_version=2,
    )
    activity = TableSpec(
        name="Activity",
        resource="activity",
        model_ref="trace_app:Activity",
        ops=tuple(
            OpSpec(
                alias=verb,
                target=verb,
                tx_scope="none",
                exchange="bidirectional_stream",
                bindings=(binding,),
            )
            for verb in ("subscribe", "publish")
        ),
    )
    router_spec = RouterSpec(
        name="realtime",
        paths=(PathSpec(path=WS_PATH, kind="ws-jsonrpc", tables=(activity,)),),
    )
    broker = InMemoryRealtimeBroker(trace_sink=timeline.add)
    spec = AppSpec(
        title="Transport Trace Lab",
        engine=sqlitef(str(database), async_=False),
        routers=(router_spec,),
    )
    app = TigrblApp.from_spec(spec, trace_sink=timeline.add, realtime_broker=broker)
    app.include_table(Note)
    app.mount_jsonrpc(prefix="/rpc")

    return app
