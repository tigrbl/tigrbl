from __future__ import annotations

import pytest

from tigrbl_core._spec import hook_spec
from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.hook_types import HookPhase


def _noop(*_args: object, **_kwargs: object) -> None:
    return None


def _matches(hook: HookSpec, metadata: dict[str, object]) -> bool:
    matcher = getattr(hook_spec, "matches_hook_selector", None)
    if matcher is None:
        pytest.xfail("runtime hook selector matcher is not implemented")
    return bool(matcher(hook, metadata))


def test_hook_selector_requires_matching_exchange_family_and_subevent() -> None:
    hook = HookSpec(
        phase=HookPhase.PRE_HANDLER,
        fn=_noop,
        exchange="server_stream",
        family=("stream",),
        subevents=("stream.chunk", "stream.end"),
    )

    assert _matches(
        hook,
        {
            "exchange": "server_stream",
            "family": "stream",
            "subevent": "stream.chunk",
        },
    )
    assert not _matches(
        hook,
        {
            "exchange": "request_response",
            "family": "stream",
            "subevent": "stream.chunk",
        },
    )
    assert not _matches(
        hook,
        {
            "exchange": "server_stream",
            "family": "request_response",
            "subevent": "stream.chunk",
        },
    )
    assert not _matches(
        hook,
        {
            "exchange": "server_stream",
            "family": "stream",
            "subevent": "response.completed",
        },
    )


def test_hook_selector_supports_wildcard_ops_and_binding_narrowing() -> None:
    hook = HookSpec(
        phase=HookPhase.POST_HANDLER,
        fn=_noop,
        ops="*",
        bindings=("public-rest", "admin-rpc"),
    )

    assert _matches(
        hook,
        {"op": "read", "binding": "public-rest", "family": "request_response"},
    )
    assert _matches(
        hook,
        {"op": "custom", "binding": "admin-rpc", "family": "rpc"},
    )
    assert not _matches(
        hook,
        {"op": "read", "binding": "private-rest", "family": "request_response"},
    )


def test_hook_selector_can_target_message_and_datagram_runtime_families() -> None:
    message_hook = HookSpec(
        phase=HookPhase.PRE_HANDLER,
        fn=_noop,
        family=("message",),
        subevents=("message.received",),
    )
    datagram_hook = HookSpec(
        phase=HookPhase.PRE_HANDLER,
        fn=_noop,
        family=("datagram",),
        subevents=("datagram.received",),
    )

    assert _matches(message_hook, {"family": "message", "subevent": "message.received"})
    assert not _matches(
        message_hook, {"family": "datagram", "subevent": "datagram.received"}
    )
    assert _matches(
        datagram_hook, {"family": "datagram", "subevent": "datagram.received"}
    )
    assert not _matches(datagram_hook, {"family": "message", "subevent": "message.received"})
