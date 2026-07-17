from .engine import S3Engine, s3_capabilities, s3_engine
from .session import S3Session


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return s3_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec=None, mapping=None):
        return s3_capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    register_engine("s3", _Registration())


__version__ = "0.4.5.dev4"
__all__ = [
    "S3Engine",
    "S3Session",
    "s3_engine",
    "s3_capabilities",
    "register",
]
