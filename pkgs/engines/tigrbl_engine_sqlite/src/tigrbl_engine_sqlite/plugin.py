from __future__ import annotations

from .engine import sqlite_capabilities, sqlite_engine


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return sqlite_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return sqlite_capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    register_engine("sqlite", _Registration())
