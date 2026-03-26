from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .pubsub import PubSubHub
from .session import PubSubSession, AsyncPubSubSession


def register() -> None:
    register_engine(kind="mempubsub", build=build_mempubsub, capabilities=capabilities)


def capabilities() -> dict:
    return {
        "engine": "mempubsub",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"topics", "fanout", "subscriptions"},
    }


def build_mempubsub(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    max_backlog = int(mapping.get("max_backlog_per_sub", 1024))
    drop_policy = str(mapping.get("drop_policy", "drop_old")).lower()
    namespace = str(mapping.get("namespace", "default"))

    engine = PubSubHub(max_backlog_per_sub=max_backlog, drop_policy=drop_policy, namespace=namespace)

    if async_:
        def sessionmaker():
            return AsyncPubSubSession(engine)
    else:
        def sessionmaker():
            return PubSubSession(engine)

    return engine, sessionmaker
