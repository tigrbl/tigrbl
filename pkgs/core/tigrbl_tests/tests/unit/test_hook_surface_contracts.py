from __future__ import annotations

from types import SimpleNamespace

import pytest

import tigrbl
from tigrbl import HookBase, hook_ctx
from tigrbl.system.diagnostics import _build_hookz_endpoint
from tigrbl_core._spec.hook_spec import (
    HookSpec,
    matches_hook_selector,
    validate_hook_legality,
    validate_hook_selector_legality,
)
from tigrbl_core._spec.hook_types import HookPhase, HookPhases


def _noop(*_args: object, **_kwargs: object) -> None:
    return None


def test_hookspec_contract_exposes_selector_and_legality_surface() -> None:
    hook = HookSpec(
        phase=HookPhase.PRE_HANDLER,
        fn=_noop,
        ops=("create", "read"),
        bindings=("http.rest",),
        framing=("json",),
        exchange="request_response",
        family=("request_response",),
        subevents=("request.received",),
        order=10,
        name="contract",
        description="contract hook",
    )

    assert hook.phase is HookPhase.PRE_HANDLER
    assert hook.ops == ("create", "read")
    assert hook.bindings == ("http.rest",)
    assert hook.framing == ("json",)
    assert hook.order == 10
    assert hook.name == "contract"
    assert hook.description == "contract hook"
    assert validate_hook_legality(hook) is None


def test_hook_selector_matches_expected_dimensions_without_cross_leakage() -> None:
    hook = HookSpec(
        phase=HookPhase.POST_HANDLER,
        fn=_noop,
        ops="*",
        bindings=("public-rest",),
        framing=("sse",),
        exchange="server_stream",
        family=("stream",),
        subevents=("stream.chunk",),
    )

    assert matches_hook_selector(
        hook,
        {
            "op": "read",
            "binding": "public-rest",
            "framing": "sse",
            "exchange": "event_stream",
            "family": "stream",
            "subevent": "stream.chunk",
        },
    )
    assert not matches_hook_selector(
        hook,
        {
            "op": "read",
            "binding": "public-rest",
            "framing": "stream",
            "exchange": "event_stream",
            "family": "stream",
            "subevent": "stream.chunk",
        },
    )
    assert not matches_hook_selector(
        hook,
        {
            "op": "read",
            "binding": "private-rest",
            "framing": "sse",
            "exchange": "event_stream",
            "family": "stream",
            "subevent": "transport.accept",
        },
    )


@pytest.mark.parametrize("phase", ("INGRESS_ROUTE", "INGRESS_DISPATCH", "POST_EMIT"))
def test_hook_legality_rejects_runtime_owned_phases(phase: str) -> None:
    hook = HookSpec(phase=phase, fn=_noop)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=phase):
        validate_hook_legality(hook)

    with pytest.raises(ValueError, match=phase):
        validate_hook_selector_legality({"phase": phase, "family": "stream"})


def test_hookbase_public_projection_is_top_level_and_spec_compatible() -> None:
    hook = HookBase(
        phase=HookPhase.POST_RESPONSE,
        fn=_noop,
        ops="read",
        framing=("json",),
        name="public_hook",
    )

    assert tigrbl.HookBase is HookBase
    assert isinstance(hook, HookSpec)
    assert hook.phase is HookPhase.POST_RESPONSE
    assert hook.ops == "read"
    assert hook.framing == ("json",)


def test_hookphase_vocabulary_exposes_only_public_hook_phases() -> None:
    public_values = {phase.value for phase in HookPhases}

    assert "PRE_HANDLER" in public_values
    assert "POST_RESPONSE" in public_values
    assert "INGRESS_ROUTE" not in HookPhase.__members__
    assert "INGRESS_DISPATCH" not in public_values
    assert "POST_EMIT" not in public_values


def test_hook_ctx_records_selector_metadata_and_attachment_ordering() -> None:
    class Widget:
        @hook_ctx(
            ops=("create", "read"),
            phase="POST_HANDLER",
            bindings=("http.rest",),
            framing="json",
            exchange="request_response",
            family="request_response",
            subevents=("request.received",),
        )
        def first(cls, ctx):
            return ctx

        @hook_ctx(ops="create", phase="POST_HANDLER")
        def second(cls, ctx):
            return ctx

    hooks = HookSpec.collect(Widget)

    assert [hook.fn.__name__ for hook in hooks] == ["first", "second"]
    assert hooks[0].ops == ("create", "read")
    assert hooks[0].bindings == ("http.rest",)
    assert hooks[0].framing == ("json",)
    assert hooks[0].family == ("request_response",)
    assert hooks[0].subevents == ("request.received",)


@pytest.mark.asyncio
async def test_hookz_mount_and_payload_project_non_empty_hook_order() -> None:
    def first(ctx):
        return ctx

    def second(ctx):
        return ctx

    class Router:
        pass

    class Model:
        pass

    Model.__name__ = "HookzModel"
    Model.hooks = SimpleNamespace(
        create=SimpleNamespace(
            PRE_HANDLER=[first, second],
            POST_RESPONSE=[],
        ),
        read=SimpleNamespace(),
    )
    Model.rpc = SimpleNamespace(create=None, read=None)

    router = Router()
    router.tables = {"HookzModel": Model}
    hookz = _build_hookz_endpoint(router)

    payload = await hookz()

    labels = payload["HookzModel"]["create"]["PRE_HANDLER"]
    assert labels[0].endswith(".first")
    assert labels[1].endswith(".second")
