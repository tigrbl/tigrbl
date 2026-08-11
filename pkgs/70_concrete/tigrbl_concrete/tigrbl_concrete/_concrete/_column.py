from __future__ import annotations

from tigrbl_base._base import ColumnBase
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.storage_spec import StorageSpec


class Column(ColumnBase):
    """Concrete SQLAlchemy column implementing a :class:`ColumnSpec`."""

    S = StorageSpec
    F = FieldSpec
    IO = IOSpec

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
