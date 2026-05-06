from __future__ import annotations

import pytest
from sqlalchemy import Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Mapped
from sqlalchemy.schema import CreateTable

from tigrbl._spec import S
from tigrbl.factories.column import acol
from tigrbl.orm.tables import TableBase


def test_postgres_storage_spec_check_compiles_to_check_constraint():
    TableBase.metadata.clear()

    class PostgresCheckedItem(TableBase):
        __tablename__ = "tigrbl_postgres_s_check_valid"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        qty: Mapped[int] = acol(storage=S(type_=Integer, nullable=False, check="qty > 0"))

    try:
        ddl = str(
            CreateTable(PostgresCheckedItem.__table__).compile(
                dialect=postgresql.dialect()
            )
        )
        assert "CONSTRAINT ck_postgrescheckeditem_qty CHECK (qty > 0)" in ddl
    finally:
        TableBase.metadata.clear()


@pytest.mark.parametrize("check_value", [["qty > 0"], {"expr": "qty > 0"}])
def test_postgres_storage_spec_check_rejects_structured_or_multiple_check_values(
    check_value,
):
    TableBase.metadata.clear()

    with pytest.raises(ArgumentError):

        class PostgresInvalidCheckItem(TableBase):
            __tablename__ = "tigrbl_postgres_s_check_invalid"
            __allow_unmapped__ = True

            id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
            qty: Mapped[int] = acol(storage=S(type_=Integer, check=check_value))

    TableBase.metadata.clear()
