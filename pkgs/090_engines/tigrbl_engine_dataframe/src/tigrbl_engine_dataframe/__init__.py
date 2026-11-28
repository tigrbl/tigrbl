"""tigrbl_engine_dataframe: DataFrame-backed Tigrbl engine"""

from .df_engine import dataframe_engine, dataframe_capabilities, DataFrameCatalog
from .df_session import TransactionalDataFrameSession

__all__ = [
    "dataframe_engine",
    "dataframe_capabilities",
    "DataFrameCatalog",
    "TransactionalDataFrameSession",
    "register",
]


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return dataframe_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return dataframe_capabilities()


def register() -> None:
    """Register the DataFrame provider with Tigrbl's current protocol."""
    from tigrbl.engine.registry import register_engine

    register_engine("dataframe", _Registration())
