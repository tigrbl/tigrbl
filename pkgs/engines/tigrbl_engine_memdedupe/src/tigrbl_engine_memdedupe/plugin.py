from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .dedupe import DedupeSet
from .session import DedupeSession, AsyncDedupeSession


def register() -> None:
    register_engine(kind="memdedupe", build=build_memdedupe, capabilities=capabilities)


def capabilities() -> dict:
    return {
        "engine": "memdedupe",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"ttl_set", "exact_membership"},
    }


def build_memdedupe(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    default_ttl_s = float(mapping.get("default_ttl_s", 60.0))
    max_items = int(mapping.get("max_items", 1_000_000))
    namespace = str(mapping.get("namespace", "default"))

    engine = DedupeSet(default_ttl_s=default_ttl_s, max_items=max_items, namespace=namespace)

    if async_:
        def sessionmaker():
            return AsyncDedupeSession(engine)
    else:
        def sessionmaker():
            return DedupeSession(engine)

    return engine, sessionmaker
