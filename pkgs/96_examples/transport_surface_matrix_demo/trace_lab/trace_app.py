"""One loopback Tigrbl application with an identity-only event buffer."""

from collections import deque
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from tigrbl import Column, TableBase, TigrblApp, TigrblRouter
from tigrbl.factories.engine import sqlitef
from tigrbl_core._spec import (
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
from tigrbl_concrete._mapping.appspec.path_lowering import _lower_router_paths
from tigrbl_engine_sqlite.plugin import register as register_sqlite
from tigrbl_kernel.identity_rollup import rollup_identity_records
from tigrbl_kernel.trace import snapshot
from tigrbl_ops_realtime import InMemoryRealtimeBroker
from tigrbl_runtime.executors import PackedPlanExecutor
from tigrbl_runtime.runtime.runtime import Runtime
from tigrbl_typing.status.exceptions import HTTPException


WS_PATH = "/ws/activity"
WT_PATH = "/wt"
FIELDS = (
    "connection_id",
    "transport_session_id",
    "session_id",
    "correlation_id",
    "opening_request_id",
    "request_id",
    "http_stream_id",
    "stream_id",
    "stream_correlation_id",
    "datagram_id",
    "subscription_id",
    "attachment_generation",
    "lease_id",
    "invocation_id",
    "attempt_id",
    "rpc_id",
    "rpc_item_index",
    "trace_id",
    "span_id",
    "parent_span_id",
    "engine_session_id",
    "transaction_id",
    "publication_id",
    "delivery_id",
    "origin_invocation_id",
    "origin_correlation_id",
    "outcome",
    "status",
    "path",
)


class Timeline:
    def __init__(self):
        self.rows = deque(maxlen=750)
        self.revision = 0

    def add(self, kind, transport, fields):
        self.revision += 1
        identity = {key: fields[key] for key in FIELDS if fields.get(key) is not None}
        self.rows.append(
            {
                "sequence": self.revision,
                "at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "kind": kind,
                "transport": transport,
                **identity,
            }
        )

    def data(self):
        rows = list(self.rows)
        return {
            "revision": self.revision,
            "events": rows,
            "rollup": rollup_identity_records(rows),
        }


class TracedExecutor(PackedPlanExecutor):
    def __init__(self, timeline):
        super().__init__()
        self.timeline = timeline

    async def _execute_packed(self, env, ctx, plan, packed):
        scope = env.scope
        try:
            return await super()._execute_packed(env, ctx, plan, packed)
        finally:
            captured = snapshot(SimpleNamespace(temp=ctx["temp"]))
            kind = {"webtransport": "WebTransport", "websocket": "WebSocket"}.get(
                scope["type"], "http"
            )
            identity = captured["identity"]
            details = {**identity, "path": scope.get("path")}
            if kind == "http":
                kind = (
                    "JSON-RPC"
                    if scope.get("path", "").rstrip("/") == "/rpc"
                    else "REST"
                )
            selection = ctx["temp"].get("webtransport_selection")
            if selection is not None:
                details["outcome"] = selection.disposition
            if identity.get("invocation_id"):
                self.timeline.add("Invocation", kind, details)
            transactions = captured["transactions"]
            links = captured["transaction_participation"]
            session = getattr(ctx, "_raw_db", None)
            if not transactions and callable(
                getattr(session, "transaction_events", None)
            ):
                # The packed fast runner can close the request-owned SQLite session
                # without populating the trace snapshot. Read the provider's retained
                # lifecycle records before discarding that invocation's context.
                transactions = session.transaction_events()
            if not links and identity.get("invocation_id"):
                links = tuple(
                    {
                        "engine_session_id": engine_id,
                        "transaction_id": transaction_id,
                    }
                    for engine_id, transaction_id in dict.fromkeys(
                        (event["engine_session_id"], event["transaction_id"])
                        for event in transactions
                    )
                )
            for transaction in transactions:
                self.timeline.add("Transaction", kind, {**details, **transaction})
            for link in links:
                self.timeline.add("Transaction participant", kind, {**details, **link})
            if scope["type"] == "webtransport":
                state = scope.get("state", {}).get("tigrbl_webtransport", {})
                events = state.get("trace", ())
                cursor = state.get("demo_trace_cursor", 0)
                for event in events[cursor:]:
                    self.timeline.add(
                        event["type"],
                        "WebTransport",
                        {**event, "path": scope.get("path")},
                    )
                state["demo_trace_cursor"] = len(events)


class TracedBroker(InMemoryRealtimeBroker):
    def __init__(self, timeline):
        super().__init__()
        self.timeline = timeline

    async def subscribe(self, **kwargs):
        subscription = await super().subscribe(**kwargs)
        self.timeline.add(
            "Subscription opened",
            "WebSocket",
            {
                **subscription.metadata,
                "subscription_id": subscription.subscription_id,
                "transport_session_id": subscription.session_id,
                "attachment_generation": subscription.generation,
            },
        )
        return subscription

    def _detach(self, subscription):
        removed = super()._detach(subscription)
        if removed:
            self.timeline.add(
                "Subscription closed",
                "WebSocket",
                {
                    **subscription.metadata,
                    "subscription_id": subscription.subscription_id,
                    "transport_session_id": subscription.session_id,
                    "attachment_generation": subscription.generation,
                },
            )
        return removed

    async def publish(self, **kwargs):
        result = await super().publish(**kwargs)
        self.timeline.add(
            "Publication",
            "WebSocket",
            {
                **kwargs,
                "publication_id": result.publication_id,
                "invocation_id": kwargs.get("origin_invocation_id"),
                "correlation_id": kwargs.get("origin_correlation_id"),
            },
        )
        return result

    def _record_delivery(self, subscription, envelope, outcome):
        super()._record_delivery(subscription, envelope, outcome)
        row = self.delivery_events()[-1]
        self.timeline.add("Delivery", "WebSocket", {**subscription.metadata, **row})


class TracedRouter(TigrblRouter):
    async def rpc_call(self, *args, **kwargs):
        context = kwargs.get("ctx") or {}
        identity = context.get("identity", {})
        try:
            result = await super().rpc_call(*args, **kwargs)
            # This runtime may return an encoded response from a bound operation.
            # The WebSocket dispatcher needs the operation's decoded JSON value.
            if isinstance(result, dict) and isinstance(result.get("body"), bytes):
                payload = json.loads(result["body"])
                if result["status_code"] >= 400:
                    raise HTTPException(
                        status_code=result["status_code"], detail=payload
                    )
                return payload
            return result
        finally:
            if identity.get("invocation_id"):
                self.__realtime_broker__.timeline.add(
                    "Invocation", "WebSocket", identity
                )


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
    broker = TracedBroker(timeline)
    router = TracedRouter()
    router.__realtime_broker__ = broker
    _lower_router_paths(router, router_spec)

    app = TigrblApp(
        title="Transport Trace Lab", engine=sqlitef(str(database), async_=False)
    )
    app.__realtime_broker__ = broker
    runtime = Runtime()
    runtime.register_executor(TracedExecutor(timeline))
    app._runtime_instance = runtime
    app.include_router(router)
    app.include_table(Note)
    app.mount_jsonrpc(prefix="/rpc")

    return app
