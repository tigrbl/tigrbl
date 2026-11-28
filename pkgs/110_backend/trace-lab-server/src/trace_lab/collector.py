"""Persist and query the trace timeline through Tigrbl table operations."""

import base64
import inspect
import json
from hashlib import sha256
from hmac import compare_digest
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import JSON, and_, cast, exists, func, or_, select, type_coerce
from sqlalchemy.dialects.postgresql import insert as insert_postgres
from sqlalchemy.dialects.sqlite import insert as insert_sqlite
from tigrbl import Column, HTTPException, TableBase, TigrblApp, op_ctx
from tigrbl_core._spec import AppSpec, HttpRestBindingSpec
from tigrbl_trace import project_event, projection_context
from tigrbl_trace.wire import MAX_BODY_BYTES, Batch

from .gateway import FAVICON_PATH, serve_frontend
from .http import reply, utc_now

INGEST_PATH = "/internal/trace/batches"
TIMELINE_PATH = "/api/timeline"
CORRELATIONS_PATH = "/api/correlations"
CORRELATION_EVENT_LIMIT = 2500
SEARCH_FIELDS = {
    "request_id",
    "rpc_id",
    "stream_correlation_id",
    "connection_id",
    "transport_session_id",
    "transaction_id",
    "invocation_id",
}


def _column(py_type, **storage):
    return Column(
        storage=Column.S(**storage),
        field=Column.F(py_type=py_type),
        io=Column.IO(),
    )


def _event_key(batch, event):
    identity = [batch.service, batch.environment, batch.worker_boot_id, event.sequence]
    return sha256(json.dumps(identity).encode()).hexdigest()


class TimelineEvent(TableBase):
    __tablename__ = "timeline_events"

    id = _column(int, primary_key=True, autoincrement=True)
    event_key = _column(str, nullable=False, unique=True)
    correlation_id = _column(str, nullable=True, index=True)
    origin_correlation_id = _column(str, nullable=True, index=True)
    captured_at = _column(str, nullable=False)
    ingested_at = _column(str, nullable=False, index=True)
    service = _column(str, nullable=False)
    environment = _column(str, nullable=False)
    worker_boot_id = _column(str, nullable=False)
    source_sequence = _column(str, nullable=False)
    kind = _column(str, nullable=False)
    transport = _column(str, nullable=False)
    identity_json = _column(str, nullable=False)

    @op_ctx(
        alias="ingest",
        target="custom",
        arity="collection",
        tx_scope="read_write",
        bindings=(
            HttpRestBindingSpec(proto="http.rest", path=INGEST_PATH, methods=("POST",)),
        ),
    )
    async def ingest(cls, ctx):
        try:
            batch = Batch.model_validate(await ctx["request"].json())
        except (ValidationError, ValueError) as error:
            raise HTTPException(422, "Invalid trace batch") from error

        now = utc_now()
        rows = [
            {
                "event_key": _event_key(batch, event),
                "service": batch.service,
                "environment": batch.environment,
                "worker_boot_id": batch.worker_boot_id,
                "source_sequence": str(event.sequence),
                "correlation_id": _identifier(event.fields.get("correlation_id")),
                "origin_correlation_id": _identifier(
                    event.fields.get("origin_correlation_id")
                ),
                "captured_at": event.captured_at.isoformat(),
                "ingested_at": now,
                "kind": event.kind,
                "transport": event.transport,
                "identity_json": json.dumps(event.fields),
            }
            for event in batch.events
        ]
        db = ctx["db"]
        table = cls.__table__
        insert = (
            insert_postgres
            if db.get_bind().dialect.name == "postgresql"
            else insert_sqlite
        )
        statement = (
            insert(table)
            .values(rows)
            .on_conflict_do_nothing(index_elements=[table.c.event_key])
            .returning(table.c.id)
        )
        inserted = (await db.execute(statement)).scalars().all()
        return {"received": len(rows), "inserted": len(inserted)}

    @op_ctx(
        alias="timeline",
        target="custom",
        arity="collection",
        tx_scope="read_only",
        bindings=(
            HttpRestBindingSpec(
                proto="http.rest", path=TIMELINE_PATH, methods=("GET",)
            ),
        ),
    )
    async def timeline(cls, ctx):
        params = ctx["request"].query_params
        try:
            limit = int(params.get("limit", 100))
            before = int(params["before"]) if "before" in params else None
        except ValueError as error:
            raise HTTPException(422, "Invalid pagination") from error
        correlation = params.get("correlation_id")
        if (
            not 1 <= limit <= 250
            or (before is not None and not 0 < before < 2**31)
            or (correlation is not None and not 1 <= len(correlation) <= 256)
        ):
            raise HTTPException(422, "Invalid timeline filters")

        table = cls.__table__
        statement = select(table)
        if before is not None:
            statement = statement.where(table.c.id < before)
        if correlation is not None:
            statement = statement.where(
                or_(
                    table.c.correlation_id == correlation,
                    table.c.origin_correlation_id == correlation,
                )
            )
        result = await ctx["db"].execute(
            statement.order_by(table.c.id.desc()).limit(limit + 1)
        )
        rows = result.mappings().all()
        events = _normalize_rows(rows[:limit])
        return {
            "events": events,
            "next_before": rows[limit - 1]["id"] if len(rows) > limit else None,
        }

    @op_ctx(
        alias="correlations",
        target="custom",
        arity="collection",
        tx_scope="read_only",
        bindings=(
            HttpRestBindingSpec(
                proto="http.rest", path=CORRELATIONS_PATH, methods=("GET",)
            ),
        ),
    )
    async def correlations(cls, ctx):
        params = ctx["request"].query_params
        value = params.get("id")
        field = params.get("id_type", "correlation_id")
        if field not in SEARCH_FIELDS | {"correlation_id"} or (
            value is not None and not 1 <= len(value) <= 520
        ):
            raise HTTPException(422, "Invalid correlation lookup")

        db = ctx["db"]
        table = cls.__table__
        c = table.c
        correlation = func.coalesce(c.correlation_id, c.origin_correlation_id)
        group_columns = (c.environment, c.service, correlation)
        anchor = select(*group_columns[:2], correlation.label("correlation"))
        anchor = anchor.where(correlation.is_not(None))
        if value is not None:
            if field == "correlation_id":
                anchor = anchor.where(
                    or_(c.correlation_id == value, c.origin_correlation_id == value)
                )
            else:
                identity = (
                    cast(c.identity_json, JSON)
                    if db.get_bind().dialect.name == "postgresql"
                    else type_coerce(c.identity_json, JSON)
                )
                match = identity[field].as_string() == value
                if field == "transaction_id" and "::" in value:
                    engine, transaction = value.rsplit("::", 1)
                    match = and_(
                        identity["engine_session_id"].as_string() == engine,
                        identity[field].as_string() == transaction,
                    )
                anchor = anchor.where(match)
        anchors = (
            anchor.group_by(*group_columns)
            .order_by(func.max(c.id).desc())
            .limit(100)
            .subquery()
        )
        matching = exists(
            select(1)
            .select_from(anchors)
            .where(
                anchors.c.environment == c.environment,
                anchors.c.service == c.service,
                or_(
                    anchors.c.correlation == c.correlation_id,
                    anchors.c.correlation == c.origin_correlation_id,
                ),
            )
        )
        if value is None:
            unassigned = (
                select(c.id)
                .where(correlation.is_(None))
                .order_by(c.id.desc())
                .limit(50)
            )
            matching = or_(matching, c.id.in_(unassigned))
        result = await db.execute(
            select(table)
            .where(matching)
            .order_by(c.id.desc())
            .limit(CORRELATION_EVENT_LIMIT + 1)
        )
        rows = result.mappings().all()
        return {
            "events": _normalize_rows(rows[:CORRELATION_EVENT_LIMIT]),
            "bounded": len(rows) > CORRELATION_EVENT_LIMIT,
        }


def _identifier(value):
    return str(value) if type(value) in (str, int) else None


def _normalize_rows(rows):
    native = [
        {
            **json.loads(row["identity_json"]),
            "sequence": row["id"],
            "at": row["captured_at"],
            "kind": row["kind"],
            "transport": row["transport"],
        }
        for row in rows
    ]
    origins = projection_context(native)
    events = []
    for saved, row in zip(rows, native, strict=True):
        event = project_event(row, origins, unclassified=True)
        events.append(
            {
                **event,
                "capture_id": saved["worker_boot_id"],
                "metadata": {
                    "service": saved["service"],
                    "environment": saved["environment"],
                    "source_sequence": saved["source_sequence"],
                    "ingested_at": saved["ingested_at"],
                    "native_transport": saved["transport"],
                    **{
                        key: row[key]
                        for key in ("trace_id", "span_id", "parent_span_id")
                        if key in row
                    },
                },
            }
        )
    return events


async def build_collector(engine):
    app = TigrblApp.from_spec(AppSpec(title="Tigrbl Trace Collector", engine=engine))
    app.include_table(TimelineEvent)
    app.mount_favicon(file_path=FAVICON_PATH)
    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized
    return app


def collector_gateway(app, frontend: Path, token: str, username: str, password: str):
    frontend = frontend.resolve()
    ingest_credential = f"Bearer {token}".encode()
    operator_credential = b"Basic " + base64.b64encode(
        f"{username}:{password}".encode()
    )

    async def gateway(scope, receive, send):
        if scope["type"] != "http":
            return await app(scope, receive, send)
        path = scope.get("path")
        method = scope.get("method")
        if path in {"/favicon.svg", "/favicon.ico"}:
            return await app(scope, receive, send)
        authorization = [
            value
            for name, value in scope["headers"]
            if name.lower() == b"authorization"
        ]
        expected = ingest_credential if path == INGEST_PATH else operator_credential
        if len(authorization) != 1 or not compare_digest(authorization[0], expected):
            challenge = (
                b"Bearer"
                if path == INGEST_PATH
                else b'Basic realm="Tigrbl Trace", charset="UTF-8"'
            )
            return await reply(
                send,
                401,
                {"error": "Authentication required"},
                headers=((b"www-authenticate", challenge),),
            )

        if path == INGEST_PATH and method == "POST":
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > MAX_BODY_BYTES:
                    return await reply(send, 413, {"error": "Trace batch too large"})
                if not message.get("more_body"):
                    break

            payload = bytes(body)

            async def replay():
                nonlocal payload
                if payload is None:
                    return await receive()
                message = {"type": "http.request", "body": payload}
                payload = None
                return message

            return await app(scope, replay, send)
        if path in {TIMELINE_PATH, CORRELATIONS_PATH}:
            return await app(scope, receive, send)
        if path in {"/", "/distributions", "/explore", "/correlations"} or (
            path and path.startswith(("/assets/", "/correlations/"))
        ):
            return await serve_frontend(
                frontend, path, method, send, reply, monitor=True
            )
        return await reply(send, 404, {"error": "Not found"})

    return gateway
