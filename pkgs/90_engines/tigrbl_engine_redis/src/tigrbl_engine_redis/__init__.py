from .engine import RedisEngine, redis_engine
from .session import RedisSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return redis_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return {
            "engine": "redis",
            "transactional": False,
            "async_native": False,
            "isolation_levels": set(),
            "read_only_enforced": False,
        }


def register() -> None:
    """Entry point hook invoked by tigrbl to register the engine kind."""
    from tigrbl.engine.registry import register_engine

    register_engine("redis", _Registration())


__all__ = [
    "RedisEngine",
    "RedisSession",
    "redis_engine",
    "register",
]
