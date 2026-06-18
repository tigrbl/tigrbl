import pytest
from types import SimpleNamespace

from tests.conftest import build_and_attach, mro_collect_decorated_ops
from tigrbl.decorators.op import op_ctx
from tigrbl.system import diagnostics as _diag


def _build_model(persist: str):
    class Model:
        __name__ = "Model"

        @op_ctx(alias="create", target="create", persist=persist)
        def custom(cls, ctx):  # pragma: no cover - execution not needed
            return None

    specs = mro_collect_decorated_ops(Model)
    Model.opspecs = SimpleNamespace(all=tuple(specs))
    build_and_attach(Model, specs)
    return Model


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "persist, expect_tx",
    [
        ("default", True),
        ("prepend", True),
        ("append", True),
        ("override", True),
        ("skip", False),
    ],
)
async def test_op_ctx_persist_options(
    monkeypatch: pytest.MonkeyPatch, persist: str, expect_tx: bool
) -> None:
    Model = _build_model(persist)
    chain = [fn.__name__ for fn in Model.hooks.create.HANDLER]
    assert chain == ["create"]

    def fake_build(model, alias):
        return {"HANDLER": Model.hooks.create.HANDLER}

    monkeypatch.setattr(_diag._default_kernel, "_build_op", fake_build)

    router = SimpleNamespace(tables={"Model": Model})
    kernelz = _diag._build_kernelz_endpoint(router)
    data = await kernelz()
    seq = data["Model"]["create"]

    if expect_tx:
        assert seq[0] == "START_TX:hook:sys:txn:begin@START_TX"
        assert seq[-1] == "TX_COMMIT:hook:sys:txn:commit@TX_COMMIT"
    else:
        assert "START_TX:hook:sys:txn:begin@START_TX" not in seq
        assert "TX_COMMIT:hook:sys:txn:commit@TX_COMMIT" not in seq
    assert any(
        item == "HANDLER:hook:wire:tigrbl:core:crud:ops:create@HANDLER"
        for item in seq
    )
