import asyncio

import pytest

from tigrbl_runtime.runtime import Runtime


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["return", "error", "cancel"])
async def test_runtime_only_forwards_original_asgi_inputs(outcome, monkeypatch):
    runtime = Runtime()
    result = object()
    error = RuntimeError("kernel error")
    cancellation = asyncio.CancelledError()
    calls = []

    class Scope(dict):
        def unexpected(self, *args, **kwargs):
            pytest.fail("runtime examined the ASGI scope")

        __getitem__ = __setitem__ = __delitem__ = __iter__ = __len__ = unexpected
        __contains__ = get = keys = items = values = copy = pop = setdefault = unexpected
        update = clear = popitem = unexpected

    async def carrier(*args):
        pytest.fail("runtime called an ASGI carrier")

    scope = Scope(type="http")
    receive = carrier

    async def send(*args):
        await carrier(*args)

    async def kernel_entry(actual_scope, actual_receive, actual_send):
        calls.append(None)
        assert actual_scope is scope
        assert actual_receive is receive
        assert actual_send is send
        if outcome == "error":
            raise error
        if outcome == "cancel":
            raise cancellation
        return result

    monkeypatch.setattr(runtime, "_asgi_entry_point", kernel_entry, raising=False)
    if outcome == "return":
        assert await runtime.dispatch_asgi(scope, receive, send) is result
    else:
        original = error if outcome == "error" else cancellation
        with pytest.raises(type(original)) as captured:
            await runtime.dispatch_asgi(scope, receive, send)
        assert captured.value is original
    assert calls == [None]
