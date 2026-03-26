from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .kv import KVStore
from .session import KVSession, AsyncKVSession


def register() -> None:
    register_engine(kind="memkv", build=build_memkv, capabilities=capabilities)


def capabilities() -> dict:
    return {
        "engine": "memkv",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"kv", "ttl_optional", "cas", "versioned"},
    }


def build_memkv(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    namespace = str(mapping.get("namespace", "default"))
    default_ttl_s = float(mapping.get("default_ttl_s", 0.0)) or None
    max_items = int(mapping.get("max_items", 1_000_000))

    engine = KVStore(namespace=namespace, default_ttl_s=default_ttl_s, max_items=max_items)

    if async_:
        def sessionmaker():
            return AsyncKVSession(engine)
    else:
        def sessionmaker():
            return KVSession(engine)

    return engine, sessionmaker
