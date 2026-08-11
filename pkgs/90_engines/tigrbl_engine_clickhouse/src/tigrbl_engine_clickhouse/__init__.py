from .engine import ClickHouseEngine, clickhouse_engine
from .session import ClickHouseSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return clickhouse_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return {
            "engine": "clickhouse",
            "transactional": False,
            "async_native": False,
            "isolation_levels": set(),
            "read_only_enforced": False,
        }


def register() -> None:
    """Entry-point hook invoked by tigrbl to register the engine kind."""
    from tigrbl.engine.registry import register_engine

    register_engine("clickhouse", _Registration())


__all__ = [
    "ClickHouseEngine",
    "ClickHouseSession",
    "clickhouse_engine",
    "register",
]
