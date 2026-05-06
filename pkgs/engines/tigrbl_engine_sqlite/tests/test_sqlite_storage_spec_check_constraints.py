from __future__ import annotations

import pytest
from sqlalchemy import Integer
from sqlalchemy.exc import ArgumentError, IntegrityError
from sqlalchemy.orm import Mapped

from tigrbl._spec import S
from tigrbl.factories.column import acol
from tigrbl.orm.tables import TableBase
from tigrbl_engine_sqlite.engine import sqlite_engine


def test_sqlite_storage_spec_check_accepts_valid_rows_and_rejects_violations():
    TableBase.metadata.clear()

    class SqliteCheckedItem(TableBase):
        __tablename__ = "tigrbl_sqlite_s_check_valid"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        qty: Mapped[int] = acol(storage=S(type_=Integer, nullable=False, check="qty > 0"))

    engine, _ = sqlite_engine()
    try:
        TableBase.metadata.create_all(engine)

        with engine.begin() as conn:
            conn.execute(SqliteCheckedItem.__table__.insert().values(id=1, qty=1))

        with pytest.raises(IntegrityError):
            with engine.begin() as conn:
                conn.execute(SqliteCheckedItem.__table__.insert().values(id=2, qty=0))
    finally:
        engine.dispose()
        TableBase.metadata.clear()


@pytest.mark.parametrize("check_value", [["qty > 0"], {"expr": "qty > 0"}])
def test_sqlite_storage_spec_check_rejects_structured_or_multiple_check_values(check_value):
    TableBase.metadata.clear()

    with pytest.raises(ArgumentError):

        class SqliteInvalidCheckItem(TableBase):
            __tablename__ = "tigrbl_sqlite_s_check_invalid"
            __allow_unmapped__ = True

            id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
            qty: Mapped[int] = acol(storage=S(type_=Integer, check=check_value))

    TableBase.metadata.clear()
