from __future__ import annotations

from typing import Any, Callable, Optional

from tigrbl_concrete._concrete._column import Column
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec as F
from tigrbl_core._spec.io_spec import IOSpec as IO
from tigrbl_core._spec.storage_spec import StorageSpec as S


def makeColumn(
    *,
    storage: S | None = None,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
    **kw: Any,
) -> Column:
    """Return a concrete :class:`Column` descriptor for declarative models."""
    if spec is not None and any(
        value is not None
        for value in (storage, field, io, default_factory, read_producer)
    ):
        raise ValueError("Provide either spec or individual components, not both.")
    if spec is None:
        if read_producer is not None and storage is not None:
            raise ValueError(
                "read_producer is only valid for virtual (storage=None) columns."
            )
        spec = ColumnSpec(
            storage=storage,
            field=field,
            io=io,
            default_factory=default_factory,
            read_producer=read_producer,
        )
    return Column(spec=spec, **kw)


def makeVirtualColumn(
    *,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    producer: Optional[Callable[[object, dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
    **kw: Any,
) -> Column:
    """Return a concrete wire-only virtual :class:`Column` descriptor."""
    if spec is not None and any(
        value is not None for value in (field, io, default_factory)
    ):
        raise ValueError("Provide either spec or individual components, not both.")
    if producer is not None and read_producer is not None:
        raise ValueError("Provide only one of producer= or read_producer=, not both.")

    resolved_producer = read_producer or producer
    if spec is not None:
        if resolved_producer is not None:
            spec = ColumnSpec(
                storage=spec.storage,
                field=spec.field,
                io=spec.io,
                default_factory=spec.default_factory,
                read_producer=resolved_producer,
            )
        return Column(spec=spec, **kw)

    return Column(
        spec=ColumnSpec(
            storage=None,
            field=field,
            io=io,
            default_factory=default_factory,
            read_producer=resolved_producer,
        ),
        **kw,
    )


acol = makeColumn
vcol = makeVirtualColumn

__all__ = [
    "Column",
    "ColumnSpec",
    "F",
    "IO",
    "S",
    "acol",
    "makeColumn",
    "makeVirtualColumn",
    "vcol",
]
