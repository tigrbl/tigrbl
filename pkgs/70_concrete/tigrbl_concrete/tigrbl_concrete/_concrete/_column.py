from __future__ import annotations

from tigrbl_base._base import ColumnBase


class Column(ColumnBase):
    """Concrete SQLAlchemy column implementing a :class:`ColumnSpec`."""

    @classmethod
    def make(cls, **kwargs):
        """Construct a concrete column through the canonical factory."""
        from tigrbl_concrete.factories.column import makeColumn

        return makeColumn(**kwargs)

    @classmethod
    def make_virtual(cls, **kwargs):
        """Construct a virtual column through the canonical factory."""
        from tigrbl_concrete.factories.column import makeVirtualColumn

        return makeVirtualColumn(**kwargs)


__all__ = ["Column"]
