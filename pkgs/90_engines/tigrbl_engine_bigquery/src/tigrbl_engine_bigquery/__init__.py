from .engine import BigQueryEngine, bigquery_engine
from .session import BigQuerySession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return bigquery_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return {
            "engine": "bigquery",
            "transactional": False,
            "async_native": False,
            "isolation_levels": set(),
            "read_only_enforced": False,
        }


def register() -> None:
    """Entry point hook invoked by tigrbl to register the engine kind."""
    from tigrbl.engine.registry import register_engine

    register_engine("bigquery", _Registration())


__all__ = [
    "BigQueryEngine",
    "BigQuerySession",
    "bigquery_engine",
    "register",
]
