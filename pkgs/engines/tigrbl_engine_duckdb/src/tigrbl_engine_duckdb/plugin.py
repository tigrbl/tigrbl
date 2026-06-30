from __future__ import annotations

from tigrbl.engine.registry import register_engine
from .duck_builder import duckdb_engine, duckdb_capabilities


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return duckdb_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return duckdb_capabilities(spec=spec, mapping=mapping)


def register() -> None:
    # Entry point hook, called by Tigrbl's plugin loader.
    # Registers the 'duckdb' engine kind.
    register_engine("duckdb", _Registration())
