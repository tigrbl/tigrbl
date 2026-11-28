from .engine import rediscachethrough_engine, rediscachethrough_capabilities
from .session import CacheThroughSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return rediscachethrough_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return rediscachethrough_capabilities()


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("rediscachethrough", _Registration())


__all__ = [
    "rediscachethrough_engine",
    "rediscachethrough_capabilities",
    "CacheThroughSession",
    "register",
]
