from .engine import mariadb_capabilities, mariadb_engine


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return mariadb_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return mariadb_capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    registration = _Registration()
    register_engine("mariadb", registration)
    register_engine("mysql", registration)

