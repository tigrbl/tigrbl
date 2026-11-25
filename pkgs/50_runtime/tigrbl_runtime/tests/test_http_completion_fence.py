from dataclasses import replace
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.transport.completion_fence import defer_http_completion
from tigrbl_runtime.executors import ExecutorBase
from tigrbl_runtime.runtime import Runtime
from tigrbl_typing.gw.raw import GwRawEnvelope


class SendExecutor(ExecutorBase):
    name = "test-http-send"

    def __init__(self, execute):
        super().__init__()
        self.execute = execute

    def should_skip_channel_prelude(self, **kwargs):
        return True

    async def invoke(self, *, runtime, env, ctx, **kwargs):
        return await self.execute(runtime, env, ctx)


def invocation(execute, send):
    async def receive():
        return {"type": "http.request", "body": b""}

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "http", "path": "/", "method": "GET"},
        receive=receive,
        send=send,
    )
    runtime = Runtime(default_executor=SendExecutor.name)
    runtime.register_executor(SendExecutor(execute))
    return runtime, env


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "trailers", "failed", "incomplete"),
    [
        (200, False, False, False),
        (500, False, False, False),
        (200, False, True, False),
        (200, False, False, True),
        (200, True, False, False),
        (200, True, False, True),
    ],
)
async def test_http_fence_is_driven_by_final_successful_carrier_send(
    status, trailers, failed, incomplete
):
    sent = []
    completions = []

    async def send(message):
        if (
            failed
            and message["type"] == "http.response.body"
            and not message.get("more_body")
        ):
            raise OSError("send failed")
        sent.append(message)

    async def execute(runtime, env, ctx):
        async def finished(completion):
            completions.append((completion.emitted, completion.status, tuple(sent)))

        defer_http_completion(env.scope, finished)
        await env.send(
            {"type": "http.response.start", "status": status, "trailers": trailers}
        )
        await env.send(
            {"type": "http.response.body", "body": b"first", "more_body": True}
        )
        assert completions == []
        if not incomplete or trailers:
            await env.send({"type": "http.response.body", "body": b"last"})
        if trailers and not incomplete:
            assert completions == []
            await env.send(
                {
                    "type": "http.response.trailers",
                    "headers": [],
                    "more_trailers": False,
                }
            )

    runtime, env = invocation(execute, send)
    ctx = {}
    if failed:
        with pytest.raises(OSError, match="send failed"):
            await runtime.invoke(env=env, ctx=ctx, plan=SimpleNamespace())
    else:
        await runtime.invoke(env=env, ctx=ctx, plan=SimpleNamespace())
    observed = not failed and not incomplete
    assert completions == [(observed, status, tuple(sent))]
    assert ctx["transport_completed"] is observed
    assert (ctx.get("current_phase") == "POST_EMIT") is observed
    assert env.send is send


@pytest.mark.asyncio
async def test_jsonrpc_batch_item_releases_actions_only_at_outer_response():
    events = []

    async def send(message):
        events.append(message["type"])

    async def execute(runtime, env, ctx):
        scope = env.scope
        if "_tigrbl_rpc_batch_item" not in scope["state"]:
            child = replace(
                env,
                scope={
                    **scope,
                    "state": {**scope["state"], "_tigrbl_rpc_batch_item": {}},
                },
                send=capture,
            )
            child_context = {}
            await runtime.invoke(env=child, ctx=child_context, plan=SimpleNamespace())
            assert events == []
            assert child_context.get("current_phase") != "POST_EMIT"
        else:
            defer_http_completion(scope, finished)
        await env.send({"type": "http.response.start", "status": 200})
        await env.send({"type": "http.response.body", "body": b""})

    async def capture(message):
        pass

    async def finished(completion):
        assert completion.emitted
        events.append("fence-released")

    runtime, env = invocation(execute, send)
    await runtime.invoke(env=env, ctx={}, plan=SimpleNamespace())
    assert events == ["http.response.start", "http.response.body", "fence-released"]
