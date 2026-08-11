from __future__ import annotations

import pytest
from tigrbl_base._base import EngineBase
from tigrbl_core._spec import EngineSessionSpec

from tigrbl_engine_memdedupe.engine import DedupeEngine
from tigrbl_engine_memdedupe.plugin import build_memdedupe, capabilities
from tigrbl_engine_memdedupe.session import DedupeSession


def test_builder_returns_engine_base_facade_and_session_factory() -> None:
    marker = object()
    engine, session_factory = build_memdedupe(
        mapping={"default_ttl_s": 15, "max_items": 20, "namespace": "tests"},
        spec=marker,
    )

    assert isinstance(engine, DedupeEngine)
    assert isinstance(engine, EngineBase)
    assert engine.spec is marker
    assert engine.to_provider() is engine
    assert engine.stats() == {
        "size": 0,
        "max_items": 20,
        "default_ttl_s": 15.0,
    }

    session_spec = EngineSessionSpec(read_only=True)
    session = session_factory(session_spec)
    assert isinstance(session, DedupeSession)
    assert session.read_only is True


@pytest.mark.asyncio
async def test_engine_rejects_statement_batches() -> None:
    engine, _ = build_memdedupe()

    with pytest.raises(TypeError, match="statement batches"):
        await engine.executeloop([])
    with pytest.raises(TypeError, match="statement batches"):
        await engine.executemany("statement", [])


def test_capabilities_describe_the_conformant_boundary() -> None:
    advertised = capabilities()

    assert advertised["engine_base"] is True
    assert advertised["session_base"] is True
    assert advertised["async_native"] is False
    assert advertised["generic_crud"] is False
    assert advertised["statement_execution"] is False
    assert "forget" in advertised["features"]
