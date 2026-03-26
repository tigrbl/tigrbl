from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .lru import LRUCache
from .session import LRUSession, AsyncLRUSession


def register() -> None:
    register_engine(kind="memlru", build=build_memlru, capabilities=capabilities)


def capabilities() -> dict:
    return {
        "engine": "memlru",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"lru", "cost_based_optional"},
    }


def build_memlru(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    max_items = int(mapping.get("max_items", 100_000))
    max_cost = float(mapping.get("max_cost", 0.0)) or None
    default_cost = float(mapping.get("default_cost", 1.0))
    namespace = str(mapping.get("namespace", "default"))

    engine = LRUCache(max_items=max_items, max_cost=max_cost, default_cost=default_cost, namespace=namespace)

    if async_:
        def sessionmaker():
            return AsyncLRUSession(engine)
    else:
        def sessionmaker():
            return LRUSession(engine)

    return engine, sessionmaker
