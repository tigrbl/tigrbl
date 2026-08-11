from sqlalchemy import Float as SQLAlchemyFloat
from tigrbl.types import Float as FacadeFloat
from tigrbl_typing.types import Float as TypingFloat


def test_float_flows_from_typing_package_to_tigrbl_types() -> None:
    assert TypingFloat is SQLAlchemyFloat
    assert FacadeFloat is TypingFloat
