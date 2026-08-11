from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .dedupe import DedupeSet
from .engine import DedupeEngine
from .session import DedupeSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return build_memdedupe(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return capabilities()


def register() -> None:
    register_engine("memdedupe", _Registration())


def capabilities() -> dict:
    return {
        "engine": "memdedupe",
        "transactional": False,
        "async_native": False,
        "persistence": "process",
        "engine_base": True,
        "session_base": True,
        "generic_crud": False,
        "statement_execution": False,
        "features": {"ttl_set", "exact_membership", "forget"},
    }


def build_memdedupe(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    default_ttl_s = float(mapping.get("default_ttl_s", 60.0))
    max_items = int(mapping.get("max_items", 1_000_000))
    namespace = str(mapping.get("namespace", "default"))

    store = DedupeSet(
        default_ttl_s=default_ttl_s,
        max_items=max_items,
        namespace=namespace,
    )
    engine = DedupeEngine(store, spec=spec)

    def sessionmaker(session_spec=None):
        return DedupeSession(engine, spec=session_spec)

    return engine, sessionmaker
