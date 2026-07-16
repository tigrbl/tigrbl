from .engine import mysql_capabilities, mysql_engine


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return mysql_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return mysql_capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    register_engine("mysql", _Registration())

