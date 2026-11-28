"""tigrbl_engine_pandas: DataFrame-backed Tigrbl engine"""

from .engine import pandas_engine, pandas_capabilities, DataFrameCatalog
from .session import TransactionalDataFrameSession

__all__ = [
    "pandas_engine",
    "pandas_capabilities",
    "DataFrameCatalog",
    "TransactionalDataFrameSession",
    "register",
]


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return pandas_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return pandas_capabilities()


def register() -> None:
    """Register the pandas provider with Tigrbl's current protocol."""
    from tigrbl.engine.registry import register_engine

    register_engine("pandas", _Registration())
