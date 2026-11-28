import importlib.util

from sqlalchemy import Float as SQLAlchemyFloat
from tigrbl_typing.types import Float


def test_package_namespace_available() -> None:
    assert importlib.util.find_spec("tigrbl_typing") is not None


def test_float_is_exported_from_typing_types() -> None:
    assert Float is SQLAlchemyFloat
