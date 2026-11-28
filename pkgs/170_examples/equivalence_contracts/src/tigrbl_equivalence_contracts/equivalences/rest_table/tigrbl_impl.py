"""Tigrbl implementation for Widget REST CRUD."""

from __future__ import annotations

from tigrbl import RestTable, TigrblApp
from tigrbl.types import Column, String


class Widget(RestTable):
    """A Widget resource authored with Tigrbl's REST table class."""

    __tablename__ = "widgets"
    __allow_unmapped__ = True
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(Widget)
app.initialize()
