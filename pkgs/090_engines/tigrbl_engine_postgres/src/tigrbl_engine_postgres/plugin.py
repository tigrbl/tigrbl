from __future__ import annotations

from .engine import postgres_capabilities, postgres_engine


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return postgres_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return postgres_capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    register_engine("postgres", _Registration())
