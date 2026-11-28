"""Concrete authoring and execution wiring for outbound operation callbacks."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from inspect import isawaitable
import json
from time import monotonic, time
from typing import TYPE_CHECKING
from uuid import uuid4

from tigrbl_atoms.atoms.transport.callback import (
    CallbackAttemptCtx,
    build_callback_payload,
)
from tigrbl_atoms.atoms.transport.completion_fence import defer_http_completion
from tigrbl_core._spec import CallbackSpec
from tigrbl_typing.trace import emit_trace, trace_fields

from ._concrete._callback import Callback
from ._decorators.callback import callback_ctx
from .factories.callback import DefineCallback
from ._runtime_services import callback_hook_phases, compile_callback_attempt

if TYPE_CHECKING:
    from .callback_attempt import CallbackAttempt


def __getattr__(name):
    if name == "CallbackAttempt":
        from .callback_attempt import CallbackAttempt

        return CallbackAttempt
    raise AttributeError(name)


def _durable_intent(spec):
    return spec.durability in {"attempts", "attempts_and_results"}


def _durable_result(spec):
    return spec.durability in {"results", "attempts_and_results"}


def _trace(sink, event, row, **fields):
    emit_trace(
        sink,
        event,
        "Callback",
        {
            **row["identity"],
            "parent_span_id": row["identity"].get("span_id"),
            "span_id": row["id"][:16],
            "delivery_id": row["delivery_id"],
            "attempt_id": row["id"],
            "attempt_number": row["attempt_number"],
            "callback_event": row["request"]["payload"]["event"],
            "source_op": row["request"].get("source_op"),
            **fields,
        },
    )


async def _prepare(spec, model, ctx):
    builder = spec.payload
    # Context decorators follow the same model method convention as hook_ctx.
    args = (
        (model, ctx)
        if getattr(builder, "__tigrbl_callback_method__", False)
        else (ctx,)
    )
    data = builder(*args)
    if isawaitable(data):
        data = await data
    if not isinstance(data, Mapping):
        raise TypeError("Callback payload builder must return a mapping")
    data = json.loads(json.dumps(dict(data), allow_nan=False))
    delivery = uuid4().hex
    temp = ctx.get("temp") or {}
    identity = trace_fields(temp.get("identity", {}))
    if "invocation_id" in identity:
        identity["origin_invocation_id"] = identity.pop("invocation_id")
    if "correlation_id" in identity:
        identity["origin_correlation_id"] = identity["correlation_id"]
    transaction_id = getattr(ctx.get("db"), "transaction_id", None)
    if transaction_id is not None:
        identity["origin_transaction_id"] = transaction_id
    return {
        "id": uuid4().hex,
        "delivery_id": delivery,
        "attempt_number": 1,
        "request": {
            "payload": build_callback_payload(
                event=spec.event, data=data, idempotency_key=delivery
            ),
            "destination": spec.destination,
            "source_op": ctx.get("op"),
            "timeout_seconds": spec.timeout_seconds,
            "max_attempts": spec.max_attempts,
            "retry_delay_seconds": spec.retry_delay_seconds,
            "signing_secret_ref": spec.signing_secret_ref,
        },
        "identity": identity,
        "status": "awaiting_emit" if spec.delivery == "after_emit" else "pending",
        "available_at": time(),
        "emit_expires_at": time() + spec.emit_wait_seconds
        if spec.delivery == "after_emit"
        else None,
        "keep_result": _durable_result(spec),
    }


async def _attempt(
    row, *, resolve_secret=None, send=None, trace_sink=None, timeout=None
):
    request = row["request"]
    row["started_at"] = time()
    started = monotonic()
    _trace(trace_sink, "callback.delivery.emit", row)
    try:
        reference = request["signing_secret_ref"]
        if reference and resolve_secret is None:
            raise ValueError("Signing resolver is unavailable")
        secret = resolve_secret(reference) if reference else None
        if isawaitable(secret):
            secret = await secret
        if reference and not isinstance(secret, str):
            raise ValueError("Signing secret is unavailable")
        delivery = CallbackAttemptCtx(
            endpoint=request["destination"],
            payload=request["payload"],
            timeout=request["timeout_seconds"] if timeout is None else timeout,
            secret=secret,
            send=send,
        )
        attempted = await compile_callback_attempt()(delivery)
        outcome = attempted.outcome
    except Exception as exc:
        outcome = {"status": "failed", "error": type(exc).__name__, "retryable": False}
    event = (
        "callback.delivery.emit_complete"
        if "http_status" in outcome
        else "callback.delivery.failed"
    )
    _trace(
        trace_sink,
        event,
        row,
        outcome=outcome["status"],
        status=outcome.get("http_status"),
        failure_class=outcome.get("error"),
        duration_ms=(monotonic() - started) * 1000,
    )
    return outcome


async def _persist(
    session_factory,
    row,
    outcome,
    *,
    retry,
    trace_sink,
    record_outcome=None,
    expired=False,
):
    from .callback_attempt import finish_attempt

    identity = {}
    try:
        following = await finish_attempt(
            session_factory,
            row,
            outcome,
            retry=retry,
            trace_identity=identity,
            record_outcome=record_outcome,
            expired=expired,
        )
    except Exception as exc:
        _trace(
            trace_sink,
            "callback.outcome.persistence_failed",
            row,
            failure_class=type(exc).__name__,
        )
        raise
    if following is None:
        _trace(trace_sink, "callback.outcome.claim_lost", row)
    else:
        _trace(
            trace_sink,
            "callback.outcome.persisted",
            row,
            outcome=outcome["status"],
            **identity,
        )
    if following:
        _trace(trace_sink, "callback.retry.scheduled", following)


async def run_callback_attempts(
    session_factory,
    *,
    resolve_secret=None,
    send=None,
    trace_sink=None,
    record_outcomes=None,
    limit=100,
):
    """Recover expired claims and execute eligible CallbackAttempt rows."""
    from .callback_attempt import claim_attempt, find_expired_attempts

    for row in await find_expired_attempts(session_factory, limit=limit):
        outcome = {"status": "unknown", "error": "expired_claim"}
        _trace(
            trace_sink,
            "callback.delivery.failed",
            row,
            outcome="unknown",
            failure_class="expired_claim",
        )
        await _persist(
            session_factory,
            row,
            outcome,
            retry=True,
            trace_sink=trace_sink,
            expired=True,
        )
    completed = 0
    for _ in range(limit):
        row = await claim_attempt(session_factory)
        if row is None:
            break
        outcome = await _attempt(
            row, resolve_secret=resolve_secret, send=send, trace_sink=trace_sink
        )
        event = row["request"]["payload"]["event"]
        recorder = (record_outcomes or {}).get(event) if row["keep_result"] else None
        await _persist(
            session_factory,
            row,
            outcome,
            retry=outcome["retryable"],
            trace_sink=trace_sink,
            record_outcome=recorder,
        )
        completed += 1
    return completed


async def _run_inline(spec, row, sink, *, source_db=None):
    if _durable_intent(spec) and source_db is None:
        from .callback_attempt import claim_attempt

        row = await claim_attempt(spec.session_factory, row["id"])
        if row is None:
            return {"status": "queued"}
    deadline = monotonic() + spec.total_timeout_seconds
    outcome = {"status": "unknown", "error": "timeout", "retryable": True}
    for number in range(1, spec.max_attempts + 1):
        remaining = deadline - monotonic()
        if remaining <= 0:
            return outcome
        outcome = await _attempt(
            row,
            resolve_secret=spec.resolve_secret,
            send=spec.send,
            trace_sink=sink,
            timeout=min(spec.timeout_seconds, remaining),
        )
        if _durable_intent(spec) and source_db is None:
            await _persist(
                spec.session_factory,
                row,
                outcome,
                retry=outcome["retryable"],
                trace_sink=sink,
                record_outcome=spec.record_outcome,
            )
            return outcome
        if source_db is not None and spec.durability != "none":
            from .callback_attempt import insert_attempt

            record = {
                **row,
                "status": outcome["status"],
                "finished_at": time(),
                "retry_exhausted": outcome["retryable"] and number == spec.max_attempts,
            }
            if not _durable_intent(spec):
                record["request"] = None
            if row["keep_result"]:
                record.update(
                    {
                        key: outcome.get(key)
                        for key in ("http_status", "response_body", "error")
                    }
                )
            await insert_attempt(source_db, record)
            if spec.record_outcome is not None:
                recorded = spec.record_outcome(
                    db=source_db, payload={**row, "outcome": outcome}
                )
                if isawaitable(recorded):
                    await recorded
        elif _durable_result(spec):
            await _persist(
                spec.session_factory,
                row,
                outcome,
                retry=False,
                trace_sink=sink,
                record_outcome=spec.record_outcome,
            )
        if not outcome["retryable"] or number == spec.max_attempts:
            return outcome
        if monotonic() + spec.retry_delay_seconds >= deadline:
            return outcome
        row = {**row, "id": uuid4().hex, "attempt_number": number + 1}
        _trace(sink, "callback.retry.scheduled", row)
        await asyncio.sleep(spec.retry_delay_seconds)
    return outcome


def lower_callback(spec, model, phase):
    """Return a context step for a kernel-selected source-operation phase."""

    async def step(ctx):
        app = ctx.get("app")
        sink = getattr(app, "trace_sink", None)
        temp = ctx.get("temp")
        if temp is None:
            temp = {}
            ctx["temp"] = temp
        rows = temp.setdefault("callback_rows", {})
        db = ctx.get("db")
        if phase == "PRE_COMMIT":
            row = await _prepare(spec, model, ctx)
            rows[id(spec)] = row
            _trace(sink, "callback.prepared", row)
            if spec.delivery == "pre_commit":
                if spec.durability != "none" and db is None:
                    raise ValueError(
                        "Durable pre-commit callback requires a source transaction"
                    )
                if spec.record_intent is not None:
                    recorded = spec.record_intent(db=db, payload=row)
                    if isawaitable(recorded):
                        await recorded
                ctx.setdefault("callback_results", {})[spec.event] = await _run_inline(
                    spec, row, sink, source_db=db
                )
            elif _durable_intent(spec):
                if db is None:
                    raise ValueError(
                        "Durable callback intent requires a source transaction"
                    )
                from .callback_attempt import insert_attempt

                await insert_attempt(db, row)
                if spec.record_intent is not None:
                    recorded = spec.record_intent(db=db, payload=row)
                    if isawaitable(recorded):
                        await recorded
            return

        if temp.get("__sys_tx_joined__"):
            # A joined transaction has not committed at this operation boundary.
            if _durable_intent(spec) and spec.delivery == "post_commit":
                return
            raise ValueError(
                "Inline after-commit callback requires a framework-owned transaction"
            )
        row = rows.get(id(spec))
        if row is None:
            row = await _prepare(spec, model, ctx)
            _trace(sink, "callback.prepared", row)
        if spec.delivery == "after_emit":
            env = ctx.get("env") or ctx.get("raw")
            scope = getattr(env, "scope", None) or getattr(
                ctx.get("request"), "scope", None
            )
            if not isinstance(scope, dict):
                raise ValueError("Callback after_emit requires an HTTP response")

            async def finish(completion):
                emitted = completion.emitted
                successful = completion.status is not None and 200 <= completion.status < 300
                eligible = emitted and successful and time() < row["emit_expires_at"]
                if _durable_intent(spec):
                    from .callback_attempt import release_attempt

                    if not await release_attempt(
                        spec.session_factory, row["id"], eligible
                    ):
                        return
                if eligible:
                    await _run_inline(spec, row, sink)
                else:
                    _trace(
                        sink,
                        "callback.delivery.cancelled",
                        row,
                        failure_class=(
                            "response_not_emitted" if not emitted else "response_ineligible"
                        ),
                    )

            defer_http_completion(scope, finish)
            return
        ctx.setdefault("callback_results", {})[spec.event] = await _run_inline(
            spec, row, sink
        )

    step.__tigrbl_label = f"hook:callback:{spec.delivery}:{spec.event}@{phase}"
    return step


def collect_callbacks(model, aliases):
    members = {}
    for base in reversed(model.__mro__):
        members.update(vars(base))
    for declaration in members.values():
        if not isinstance(declaration, CallbackSpec):
            continue
        ops = (
            (declaration.ops,) if isinstance(declaration.ops, str) else declaration.ops
        )
        for alias in ops:
            if alias not in aliases:
                raise ValueError(
                    f"Callback source operation {alias!r} is not declared on {model.__name__}"
                )
            for phase in callback_hook_phases(
                declaration.delivery, durable_intent=_durable_intent(declaration)
            ):
                yield alias, phase, lower_callback(declaration, model, phase)


__all__ = [
    "Callback",
    "CallbackAttempt",
    "CallbackSpec",
    "DefineCallback",
    "callback_ctx",
    "run_callback_attempts",
]
