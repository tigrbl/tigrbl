import pytest

from tigrbl import DefineCallback, callback_ctx
from tigrbl_concrete.callbacks import collect_callbacks
from tigrbl_kernel.callbacks import callback_hook_phases


def test_callback_factory_and_context_decorator_lower_identically():
    options = dict(
        ops="mark_paid", event="invoice.paid", destination="https://example.test/hooks"
    )

    class Factory:
        notify = DefineCallback(payload=lambda ctx: {}, **options)

    class Decorated:
        @callback_ctx(**options)
        def notify(cls, ctx):
            return {}

    def plan(model):
        return [
            (alias, phase, hook.__tigrbl_label)
            for alias, phase, hook in collect_callbacks(model, {"mark_paid", "create"})
        ]

    assert (
        plan(Factory)
        == plan(Decorated)
        == [
            (
                "mark_paid",
                "POST_COMMIT",
                "hook:callback:post_commit:invoice.paid@POST_COMMIT",
            )
        ]
    )
    with pytest.raises(ValueError, match="not declared"):
        list(collect_callbacks(Factory, {"create"}))


def test_callback_phase_placement_and_private_completion_fence():
    assert callback_hook_phases("pre_commit", durable_intent=True) == ("PRE_COMMIT",)
    assert callback_hook_phases("worker", durable_intent=True) == ("PRE_COMMIT",)
    assert callback_hook_phases("post_commit", durable_intent=True) == (
        "PRE_COMMIT",
        "POST_COMMIT",
    )
    assert callback_hook_phases("after_emit", durable_intent=False) == ("POST_COMMIT",)
    with pytest.raises(ValueError, match="durable intent"):
        callback_hook_phases("worker", durable_intent=False)
