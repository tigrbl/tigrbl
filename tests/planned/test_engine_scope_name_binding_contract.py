import pytest

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.engine_spec import EngineSpec
from tigrbl_core._spec.op_spec import OpSpec


def test_engine_scope_name_binding_contract() -> None:
    AppSpec(
        engines=(EngineSpec(kind="sqlite", memory=True, name="primary"),),
        ops=(OpSpec(alias="read", target="read", engine_name="primary"),),
    )

    with pytest.raises(ValueError, match="unknown engine name"):
        AppSpec(
            engines=(EngineSpec(kind="sqlite", memory=True, name="primary"),),
            ops=(OpSpec(alias="read", target="read", engine_name="missing"),),
        )
