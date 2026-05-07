import pytest

from tigrbl_base._base._engine_base import EngineBase


def test_engine_base_to_provider_not_implemented() -> None:
    engine = EngineBase()

    try:
        engine.to_provider()
    except NotImplementedError:
        assert True
    else:
        raise AssertionError("Expected NotImplementedError")


@pytest.mark.asyncio
async def test_engine_base_batch_methods_default_to_not_implemented() -> None:
    engine = EngineBase()

    with pytest.raises(NotImplementedError):
        await engine.executeloop([])

    with pytest.raises(NotImplementedError):
        await engine.executemany("INSERT", [])
