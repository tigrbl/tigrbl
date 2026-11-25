import asyncio
import inspect
import hashlib
import hmac

import httpx
import pytest

from tigrbl import (
    HTTPException,
    Request,
    TableBase,
    TigrblApp,
    callback_ctx,
    op_ctx,
    webhook_ctx,
)


async def _build_receiver(events):
    app = TigrblApp()

    def verify(request: Request):
        digest = hmac.new(b"demo", request.body, hashlib.sha256).hexdigest()
        if request.headers["x-webhook-signature"] != f"sha256={digest}":
            raise HTTPException(status_code=401, detail="Invalid signature")
        return True

    @webhook_ctx(
        path="/hooks", provider="test", event_type="paid", security_deps=(verify,)
    )
    def received(ctx):
        events.append(("callback", ctx["payload"]["data"]))
        return {"accepted": True}

    app.include_webhook(received)
    init = app.initialize()
    if inspect.isawaitable(init):
        await init
    return app


@pytest.mark.asyncio
@pytest.mark.parametrize("timing", ["post_commit", "after_emit"])
async def test_callback_and_original_response_order(timing):
    events = []
    receiver = await _build_receiver(events)

    async def send(endpoint, body, headers, timeout):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=receiver)
        ) as client:
            result = await client.post(endpoint, content=body, headers=headers)
        return {"status_code": result.status_code}

    class Invoice(TableBase):
        @op_ctx(alias="pay", target="custom", arity="collection", persist="skip")
        def pay(cls, ctx):
            return {"invoice_id": "inv-1"}

        @callback_ctx(
            ops="pay",
            event="paid",
            destination="https://test/hooks",
            delivery=timing,
            send=send,
            signing_secret_ref="billing",
            resolve_secret=lambda ref: "demo",
        )
        def notify(cls, ctx):
            return ctx["result"]

    app = TigrblApp()
    app.include_table(Invoice)
    init = app.initialize()
    if inspect.isawaitable(init):
        await init

    async def observe(scope, receive, send_response):
        async def capture(message):
            await send_response(message)
            if message["type"] == "http.response.body" and not message.get("more_body"):
                events.append(("response", None))

        await app(scope, receive, capture)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=observe), base_url="https://test"
    ) as client:
        result = await client.post("/invoice/pay", json={})
    assert result.status_code == 200, result.text
    assert result.json() == {"invoice_id": "inv-1"}
    callback = ("callback", {"invoice_id": "inv-1"})
    response = ("response", None)
    assert events == (
        [callback, response] if timing == "post_commit" else [response, callback]
    )

    if timing == "after_emit":

        async def fail_to_send(scope, receive, send_response):
            async def broken_send(message):
                if message["type"] == "http.response.body":
                    raise OSError("requester disconnected")

            await app(scope, receive, broken_send)

        events.clear()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=fail_to_send), base_url="https://test"
        ) as client:
            with pytest.raises(OSError, match="disconnected"):
                await client.post("/invoice/pay", json={})
        assert events == []


@pytest.mark.asyncio
async def test_emitted_error_response_does_not_release_success_only_callback():
    from types import SimpleNamespace

    from tigrbl import CallbackSpec
    from tigrbl_atoms.atoms.transport.completion_fence import (
        finish_http_completion,
        observe_http_completion,
    )
    from tigrbl_concrete.callbacks import lower_callback

    events = []

    async def send(*args):
        events.append("callback")
        return {"status_code": 202}

    async def response_send(message):
        events.append(message["type"])

    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {},
        delivery="after_emit",
        send=send,
    )
    env = SimpleNamespace(scope={"type": "http"}, send=response_send)
    ctx = {"env": env, "temp": {}}
    with observe_http_completion(env) as completion:
        await lower_callback(spec, object, "POST_COMMIT")(ctx)
        await env.send({"type": "http.response.start", "status": 500})
        await env.send({"type": "http.response.body", "body": b"error"})
        await finish_http_completion(env.scope, ctx, completion)
    assert ctx["current_phase"] == "POST_EMIT"
    assert events == ["http.response.start", "http.response.body"]


@pytest.mark.asyncio
async def test_worker_callback_is_created_by_the_mounted_source_operation(tmp_path):
    from sqlalchemy import Column, String, create_engine, select
    from sqlalchemy.orm import sessionmaker
    from tigrbl import DefineCallback, run_callback_attempts
    from tigrbl.factories.engine import sqlitef
    from tigrbl_concrete.callbacks import CallbackAttempt
    from tigrbl_kernel.core import Kernel

    path = tmp_path / "mounted-worker.db"
    engine = create_engine(f"sqlite:///{path}")
    CallbackAttempt.__table__.create(engine)
    sessions = sessionmaker(engine)
    sent = []

    class Payment(TableBase):
        __tablename__ = "callback_source_payment"
        id = Column(String, primary_key=True)

        @op_ctx(alias="pay", target="custom", arity="collection")
        def pay(cls, ctx):
            ctx["db"].add(cls(id="invoice-1"))
            return {"invoice_id": "invoice-1"}

        notify = DefineCallback(
            ops="pay",
            event="paid",
            destination="https://test/hooks",
            payload=lambda ctx: ctx["result"],
            delivery="worker",
            durability="attempts_and_results",
            session_factory=sessions,
        )

    app = TigrblApp(engine=sqlitef(str(path)))
    app.include_table(Payment)
    init = app.initialize()
    if inspect.isawaitable(init):
        await init
    assert any(
        "hook:callback:worker:paid@PRE_COMMIT" in label
        for label in Kernel().plan_labels(Payment, "pay")
    )

    async def send(endpoint, body, headers, timeout):
        sent.append(headers["Idempotency-Key"])
        return {"status_code": 202}

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://test"
    ) as client:
        reply = await client.post("/payment/pay", json={})
    assert reply.status_code == 200, reply.text
    assert sent == []
    with sessions() as db:
        assert db.scalar(select(Payment.id)) == "invoice-1"
        delivery_id = db.scalar(select(CallbackAttempt.delivery_id))
        assert db.scalar(select(CallbackAttempt.status)) == "pending"
    assert await run_callback_attempts(sessions, send=send) == 1
    assert sent == [delivery_id]
    with sessions() as db:
        assert db.scalar(select(CallbackAttempt.status)) == "delivered"
    engine.dispose()


@pytest.mark.asyncio
async def test_callback_attempt_timeout_is_an_unknown_outcome():
    from tigrbl_runtime.callbacks import attempt_callback

    async def slow_send(*args):
        await asyncio.sleep(10)

    outcome = await attempt_callback(
        "https://test/hooks",
        {"idempotency_key": "event-1"},
        timeout=0.01,
        send=slow_send,
    )
    assert outcome == {"status": "unknown", "error": "timeout", "retryable": True}


@pytest.mark.asyncio
async def test_default_callback_sender_posts_signed_bytes_to_loopback():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from threading import Thread

    from tigrbl_runtime.callbacks import attempt_callback

    received = []

    class Receiver(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            received.append((self.path, body, self.headers["X-Webhook-Signature"]))
            self.send_response(202)
            self.end_headers()

    with HTTPServer(("127.0.0.1", 0), Receiver) as server:
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            outcome = await attempt_callback(
                f"http://127.0.0.1:{server.server_port}/hooks?scope=local",
                {"idempotency_key": "delivery", "event": "paid"},
                timeout=3,
                secret="demo",
            )
        finally:
            server.shutdown()
            worker.join()
    assert outcome["http_status"] == 202
    path, body, signature = received[0]
    assert path == "/hooks?scope=local"
    assert signature == "sha256=" + hmac.new(b"demo", body, hashlib.sha256).hexdigest()
