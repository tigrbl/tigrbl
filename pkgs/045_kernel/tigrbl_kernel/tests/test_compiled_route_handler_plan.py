import inspect
from types import SimpleNamespace

import pytest

from tigrbl_atoms.route_handler import RouteHandlerDeclaration
from tigrbl_kernel import Kernel


@pytest.mark.asyncio
async def test_compiled_handler_carries_identity_and_never_rebinds_signature(monkeypatch):
    class RouteRegistry(dict):
        def get(self, key, default=None):
            pytest.fail("compiled handler looked up the concrete route")

    class Model:
        __tigrbl_route_registry__ = RouteRegistry()

    class Context(SimpleNamespace):
        def get(self, key, default=None):
            return getattr(self, key, default)

    def dependency():
        return "dependency"

    request = object()
    marker = SimpleNamespace(dependency=dependency)

    async def handle(item, request, ctx, loaded=marker):
        assert loaded == "dependency"
        return item, request, ctx

    declaration = RouteHandlerDeclaration(handle, lambda ctx: request, 202)
    Model.hooks = SimpleNamespace(show=SimpleNamespace(HANDLER=[declaration]))
    signature = inspect.signature
    inspections = []

    def count_signature(target, **kwargs):
        if target is handle:
            inspections.append(target)
            assert len(inspections) == 1
        return signature(target, **kwargs)

    monkeypatch.setattr(inspect, "signature", count_signature)
    chain = Kernel()._build_op(Model, "show")["HANDLER"]
    step, = (item for item in chain if hasattr(item, "_tigrbl_route_handler_plan"))
    plan = step._tigrbl_route_handler_plan
    assert plan.model is Model
    assert plan.alias == "show"
    assert plan.declaration.handler is handle
    assert [(arg.name, arg.source) for arg in plan.arguments] == [
        ("item", "path"),
        ("request", "request"),
        ("ctx", "context"),
        ("loaded", "dependency"),
    ]

    ctx = Context(model=Model, op="show", path_params={"item": "one"}, temp={})
    await step(ctx)
    assert ctx.result == ("one", request, ctx)
    assert ctx.status_code == 202
    assert inspections == [handle]
