from __future__ import annotations

from .engine import InMemoryEngine
from .session import AsyncInMemorySession, InMemorySession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return build_inmemory(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        del spec, mapping
        return capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    register_engine("inmemory", _Registration())


def capabilities() -> dict:
    return {
        "engine": "inmemory",
        "transactional": True,
        "async_native": True,
        "isolation_levels": {"snapshot"},
        "read_only_enforced": False,
        "persistence": "process",
    }


def build_inmemory(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    del dsn
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))
    engine = InMemoryEngine(
        namespace=str(mapping.get("namespace", "default")),
        enforce_schema=bool(mapping.get("enforce_schema", False)),
    )
    if async_:

        def sessionmaker():
            return AsyncInMemorySession(engine)
    else:

        def sessionmaker():
            return InMemorySession(engine)

    return engine, sessionmaker