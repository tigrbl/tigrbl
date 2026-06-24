import pytest

from tigrbl_runtime.executors.invoke import _invoke


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
