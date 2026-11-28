import asyncio
import json
from types import SimpleNamespace

import pytest

from tigrbl import Depends, Request, Response, StreamingResponse, TigrblApp


async def _call(app, path, sent):
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    await app(
        {"type": "http", "method": "GET", "path": path, "headers": [], "query_string": b""},
        receive,
        send,
    )


def _assert_response(sent, status, body):
    starts = [event for event in sent if event["type"] == "http.response.start"]
    bodies = [event for event in sent if event["type"] == "http.response.body"]
    assert len(starts) == 1 and sent[0] is starts[0]
    assert starts[0]["status"] == status
    assert [event for event in bodies if not event.get("more_body")] == [sent[-1]]
    assert b"".join(event["body"] for event in bodies) == body
    return starts[0]["headers"]


@pytest.mark.asyncio
@pytest.mark.parametrize("template", [False, True], ids=["exact", "templated"])
@pytest.mark.parametrize("async_handler", [False, True], ids=["sync", "async"])
async def test_compiled_handler_keeps_argument_and_operation_parity(
    monkeypatch, template, async_handler
):
    app = TigrblApp()
    calls = []
    path = "/items/one"

    def handle(request, ctx, item="default"):
        assert isinstance(request, Request)
        calls.append((ctx.model, ctx.op, item, request.path, dict(request.path_params)))
        return {"item": item}

    async def async_handle(request, ctx, item="default"):
        return handle(request, ctx, item)

    app.add_route(
        "/items/{item}" if template else path,
        async_handle if async_handler else handle,
        name="show_item",
        methods=("GET",),
    )
    executor = app.runtime.executors["packed"]
    exact = executor._prime_exact_route_program
    selections = []

    def select_exact(*args):
        result = exact(*args)
        selections.append(result)
        return result

    probes = []
    probe = executor._probe_ingress_for_program

    async def record_probe(*args):
        result = await probe(*args)
        probes.append(result)
        return result

    monkeypatch.setattr(executor, "_prime_exact_route_program", select_exact)
    monkeypatch.setattr(executor, "_probe_ingress_for_program", record_probe)
    sent = []
    await _call(app, path, sent)
    assert len(calls) == 1
    assert len(selections) == 1
    if template:
        assert selections[0] < 0
        assert len(probes) == 1 and probes[0] >= 0
    else:
        assert selections[0] >= 0
        assert not probes

    program_id = probes[0] if template else selections[0]
    model, alias, item, request_path, params = calls[0]
    plan, _ = app.runtime.compile(app)
    meta = plan.opmeta[program_id]
    assert (model, alias) == (meta.model, meta.alias)
    assert item == ("one" if template else "default")
    assert request_path == path
    assert params == ({"item": "one"} if template else {})
    assert json.loads(sent[-1]["body"]) == {"item": item}
    _assert_response(sent, 200, sent[-1]["body"])

    # Force a fallback for the same operation and compare the complete binding.
    monkeypatch.setattr(executor, "_prime_exact_route_program", lambda *args: -1)
    fallback = []
    await _call(app, path, fallback)
    assert probes[-1] == program_id
    assert len(calls) == 2 and calls[1] == calls[0]
    assert json.loads(fallback[-1]["body"]) == {"item": item}
    _assert_response(fallback, 200, fallback[-1]["body"])


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["success", "handler-error", "acquisition-error", "cancel"])
async def test_compiled_dependencies_teardown_in_reverse_order(outcome):
    app = TigrblApp()
    events = []
    entered = asyncio.Event()

    def original():
        pytest.fail("dependency override was bypassed")

    def override():
        events.append("sync-enter")
        try:
            yield "sync"
        finally:
            events.append("sync-exit")

    async def second():
        events.append("async-enter")
        try:
            if outcome == "acquisition-error":
                raise RuntimeError("broken dependency")
            yield "async"
        finally:
            events.append("async-exit")

    @app.get("/dependencies")
    async def handle(first=Depends(original), last=Depends(second)):
        assert (first, last) == ("sync", "async")
        events.append("handler")
        if outcome == "handler-error":
            raise RuntimeError("broken handler")
        if outcome == "cancel":
            entered.set()
            await asyncio.Future()
        return {"ok": True}

    app.runtime.compile(app)
    app.dependency_overrides = {original: override}
    sent = []
    if outcome == "cancel":
        task = asyncio.create_task(_call(app, "/dependencies", sent))
        try:
            await asyncio.wait_for(entered.wait(), timeout=3)
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert sent == []
    else:
        await _call(app, "/dependencies", sent)
        assert sent[0]["status"] == (200 if outcome == "success" else 500), sent
    handler_events = [] if outcome == "acquisition-error" else ["handler"]
    assert events == ["sync-enter", "async-enter", *handler_events, "async-exit", "sync-exit"]


@pytest.mark.asyncio
@pytest.mark.parametrize("concrete", [True, False], ids=["concrete", "response-like"])
async def test_compiled_handler_emits_plain_and_response_like_results(concrete):
    app = TigrblApp()

    @app.get("/plain", status_code=201)
    def plain():
        return {"ok": True}

    @app.get("/response")
    async def response():
        if concrete:
            return Response(status_code=202, headers={"x-marker": "one"}, body=b"raw")
        return SimpleNamespace(
            status_code=202,
            raw_headers=[(b"x-marker", b"one"), (b"x-marker", b"two")],
            body=b"raw",
        )

    sent = []
    await _call(app, "/plain", sent)
    assert json.loads(sent[-1]["body"]) == {"ok": True}
    _assert_response(sent, 201, sent[-1]["body"])

    sent = []
    await _call(app, "/response", sent)
    headers = _assert_response(sent, 202, b"raw")
    expected = [b"one"] if concrete else [b"one", b"two"]
    assert [value for name, value in headers if name == b"x-marker"] == expected


@pytest.mark.asyncio
async def test_compiled_handler_streams_before_the_producer_finishes():
    app = TigrblApp()
    first_sent = asyncio.Event()
    resume = asyncio.Event()

    async def content():
        yield b"one"
        await resume.wait()
        yield b"two"

    @app.get("/stream")
    async def stream():
        return StreamingResponse(content(), status_code=202, headers={"x-marker": "stream"})

    class ObservedEvents(list):
        def append(self, event):
            super().append(event)
            if event.get("body") == b"one":
                first_sent.set()

    sent = ObservedEvents()
    task = asyncio.create_task(_call(app, "/stream", sent))
    try:
        await asyncio.wait_for(first_sent.wait(), timeout=3)
        assert not task.done()
        assert sent[-1]["more_body"] is True
    finally:
        resume.set()
        await asyncio.wait_for(task, timeout=3)
    headers = _assert_response(sent, 202, b"onetwo")
    assert (b"x-marker", b"stream") in headers
    assert [event["body"] for event in sent if event.get("more_body")] == [b"one", b"two"]
