from .engine import S3FSEngine, s3fs_capabilities, s3fs_engine
from .session import S3FSSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return s3fs_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec=None, mapping=None):
        return s3fs_capabilities()


def register() -> None:
    from tigrbl.engine.registry import register_engine

    register_engine("s3fs", _Registration())


__version__ = "0.4.5.dev4"
__all__ = [
    "S3FSEngine",
    "S3FSSession",
    "s3fs_engine",
    "s3fs_capabilities",
    "register",
]
