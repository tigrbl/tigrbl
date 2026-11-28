from __future__ import annotations
from typing import Any, Callable, Tuple, Optional, Dict
from pyspark.sql import SparkSession

from .session import PySparkSession


def pyspark_engine(
    app_name: str = "tigrbl-pyspark",
    conf: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Tuple[Any, Callable[[], Any]]:
    """Build the underlying SparkSession and return (engine, session_factory)."""
    builder = SparkSession.builder.appName(app_name)
    for k, v in (conf or {}).items():
        builder = builder.config(k, v)
    spark = builder.getOrCreate()

    def session_factory() -> PySparkSession:
        return PySparkSession(spark)

    return spark, session_factory


def pyspark_capabilities() -> dict:
    return {
        "sql": True,
        "dataframe": True,
        "transactions": False,
        "distributed": True,
        "dialect": "spark-sql",
    }
