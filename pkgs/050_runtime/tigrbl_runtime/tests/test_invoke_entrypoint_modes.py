import pytest

from tigrbl_runtime.executors.phase_runner import _invoke
from tigrbl_runtime.executors import kernel_executor
from tigrbl_typing.status.exceptions import HTTPException


@pytest.mark.asyncio
@pytest.mark.parametrize("fail_phase", [None, "SECURITY", "HANDLER", "TX_COMMIT"])
async def test_invocation_outcome_preserves_empty_success_or_authoritative_failure(
    monkeypatch, fail_phase
):
    events = []

    def step(phase):
        def run(ctx):
            events.append(phase)
            if phase == fail_phase:
                raise HTTPException(403 if phase == "SECURITY" else 409, phase)
        return run

    ordered = ["SECURITY", "HANDLER", "TX_COMMIT"]
    monkeypatch.setattr(
        kernel_executor, "resolve_phase_chains",
        lambda model, alias: {phase: [step(phase)] for phase in ordered},
    )
    model = type("Record", (), {})
    context = {"specs": {}, "opview": object()}
    if fail_phase is None:
        assert await kernel_executor.invoke_op(model=model, alias="delete", ctx=context) is None
        assert events == ordered
    else:
        with pytest.raises(HTTPException) as error:
            await kernel_executor.invoke_op(model=model, alias="delete", ctx=context)
        assert events == ordered[:ordered.index(fail_phase) + 1]
        assert error.value.status_code == (403 if fail_phase == "SECURITY" else 409)


@pytest.mark.asyncio
async def test_missing_invocation_plan_fails_closed(monkeypatch):
    monkeypatch.setattr(kernel_executor, "resolve_phase_chains", lambda model, alias: {})
    with pytest.raises(LookupError, match="No compiled operation"):
        await kernel_executor.invoke_op(
            model=type("Record", (), {}), alias="delete", ctx={"specs": {}, "opview": object()}
        )


@pytest.mark.asyncio
async def test_invoke_can_run_dispatch_mode_without_ingress_or_egress() -> None:
    events: list[str] = []

    def step(name):
        def _run(ctx):
            events.append(name)
            if name == "HANDLER":
                ctx.result = {"ok": True}

        return _run

    result = await _invoke(
        request=None,
        db=None,
        phases={
            "INGRESS_BEGIN": [step("INGRESS_BEGIN")],
            "INGRESS_PARSE": [step("INGRESS_PARSE")],
            "INGRESS_ROUTE": [step("INGRESS_ROUTE")],
            "PRE_TX_BEGIN": [step("PRE_TX_BEGIN")],
            "HANDLER": [step("HANDLER")],
            "POST_COMMIT": [step("POST_COMMIT")],
            "POST_RESPONSE": [step("POST_RESPONSE")],
            "EGRESS_SHAPE": [step("EGRESS_SHAPE")],
            "EGRESS_FINALIZE": [step("EGRESS_FINALIZE")],
        },
        ctx={
            "skip_ingress": True,
            "skip_egress": True,
            "skip_post_commit": True,
        },
    )

    assert result == {"ok": True}
    assert events == ["PRE_TX_BEGIN", "HANDLER"]
