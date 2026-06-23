"""Tigrbl implementation for the TableBase table-class equivalence."""

from __future__ import annotations

from tigrbl import TableBase, TigrblApp
from tigrbl.types import Column, String


class WidgetTableBase(TableBase):
    """A Widget resource authored with Tigrbl TableBase."""

    __tablename__ = "widgets_table_base"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetTableBase)
app.initialize()
