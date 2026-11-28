import re
import time

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session

from tigrbl.orm.mixins import ULIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.schema import _build_schema


@pytest.fixture
def widget():
    class Widget(TableBase, ULIDPk):
        __tablename__ = "ulid_widgets"

    return Widget


@pytest.fixture
def session(widget):
    with create_engine("sqlite://").connect() as connection:
        widget.__table__.create(connection)
        with Session(connection) as session:
            yield session


def test_ulid_primary_key_defaults_and_round_trips(widget, session):
    supplied_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    first, second = widget(), widget()
    session.add_all([first, second, widget(id=supplied_id)])

    before_ms = time.time_ns() // 1_000_000
    session.flush()
    after_ms = time.time_ns() // 1_000_000

    assert first.id != second.id
    assert re.fullmatch(r"[0-7][0-9A-HJKMNP-TV-Z]{25}", first.id)
    timestamp_ms = 0
    for char in first.id[:10]:
        timestamp_ms = timestamp_ms * 32 + "0123456789ABCDEFGHJKMNPQRSTVWXYZ".index(
            char
        )
    assert before_ms <= timestamp_ms <= after_ms
    session.expunge_all()
    assert session.get(widget, first.id).id == first.id
    assert session.get(widget, supplied_id).id == supplied_id
    assert "id" not in _build_schema(widget, verb="create").model_fields
    assert (
        _build_schema(widget, verb="update").model_validate({"id": supplied_id}).id
        == supplied_id
    )


@pytest.mark.parametrize(
    "invalid",
    [
        "01ARZ3NDEKTSV4RRFFQ69G5FA",
        "01ARZ3NDEKTSV4RRFFQ69G5FAI",
        "81ARZ3NDEKTSV4RRFFQ69G5FAV",
        "01arz3ndektsv4rrffq69g5fav",
        "01ARZ3NDEKTSV4RRFFQ69G5FAV\n",
    ],
)
def test_ulid_primary_key_rejects_noncanonical_values(widget, session, invalid):
    update_schema = _build_schema(widget, verb="update")
    with pytest.raises(ValidationError):
        update_schema.model_validate({"id": invalid})

    session.add(widget(id=invalid))
    with pytest.raises(StatementError, match="canonical 26-character uppercase ULID"):
        session.flush()
