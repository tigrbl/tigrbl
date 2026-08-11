from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .queuehub import QueueHub
from .session import QueueSession, AsyncQueueSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return build_memqueue(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return capabilities()


def register() -> None:
    register_engine("memqueue", _Registration())


def capabilities() -> dict:
    return {
        "engine": "memqueue",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"fifo", "lifo", "priority_optional", "named_queues"},
    }


def build_memqueue(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    mode = str(mapping.get("mode", "fifo")).lower()
    max_items = int(mapping.get("max_items", 100_000))
    namespace = str(mapping.get("namespace", "default"))

    engine = QueueHub(mode=mode, max_items=max_items, namespace=namespace)

    if async_:
        def sessionmaker():
            return AsyncQueueSession(engine)
    else:
        def sessionmaker():
            return QueueSession(engine)

    return engine, sessionmaker
