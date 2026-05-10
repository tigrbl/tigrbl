import pytest

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.engine_spec import EngineSpec


def test_appspec_engine_inventory_contract() -> None:
    app = AppSpec(
        engines=(
            EngineSpec(kind="sqlite", memory=True, name="primary"),
            EngineSpec(kind="postgres", name="warehouse"),
        )
    )

    assert [engine.name for engine in app.engines] == ["primary", "warehouse"]

    with pytest.raises(ValueError, match="Duplicate EngineSpec.name"):
        AppSpec(
            engines=(
                EngineSpec(kind="sqlite", memory=True, name="primary"),
                EngineSpec(kind="postgres", name="primary"),
            )
        )
