import pytest

from tigrbl import build_handlers, hook_ctx, op_ctx
from tigrbl_core._spec.op_spec import resolve
from tigrbl.orm.tables import TableBase


@pytest.mark.asyncio
async def test_handlers_bind_core_dispatch_and_invoke_entrypoints() -> None:
    events: list[str] = []

    class Widget(TableBase):
        @op_ctx(alias="ping", target="custom", arity="collection", persist="skip")
        def ping(cls, ctx):
            events.append(f"core:{ctx.get('model') is Widget}:{ctx.get('op')}")
            return {"ok": True}

        @hook_ctx(ops="ping", phase="PRE_TX_BEGIN")
        def pre_tx_begin(cls, ctx):
            events.append(f"pre_tx:{ctx.get('model') is Widget}:{ctx.get('op')}")

        @hook_ctx(ops="ping", phase="POST_COMMIT")
        def post_commit(cls, ctx):
            events.append("post_commit")
            ctx["post_commit"] = True

        @hook_ctx(ops="ping", phase="POST_RESPONSE")
        def post_response(cls, ctx):
            events.append("post_response")
            ctx.response.result["post_response"] = True

    specs = resolve(Widget)
    build_handlers(Widget, specs)

    handlers = Widget.handlers.ping
    assert callable(handlers.invoke)
    assert callable(handlers.dispatch)
    assert callable(handlers.core)
    assert callable(handlers.raw)
    assert callable(handlers.handler)
    assert callable(handlers.core_raw)

    assert await handlers.core({"payload": {"value": 1}}) == {"ok": True}
    assert events == ["core:True:ping"]

    events.clear()
    assert await handlers.dispatch({"payload": {"value": 2}}) == {"ok": True}
    assert events == ["pre_tx:True:ping", "core:True:ping"]

    events.clear()
    assert await handlers.invoke({"payload": {"value": 3}}) == {
        "ok": True,
        "post_response": True,
    }
    assert events == [
        "pre_tx:True:ping",
        "core:True:ping",
        "post_commit",
        "post_response",
    ]
