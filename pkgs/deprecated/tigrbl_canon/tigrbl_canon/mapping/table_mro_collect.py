from __future__ import annotations

from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)


from functools import lru_cache

from tigrbl_core._spec.table_spec import TableSpec


@lru_cache(maxsize=None)
def mro_collect_table_spec(model: type) -> TableSpec:
    """Collect TableSpec-like declarations across the model's MRO."""
    return TableSpec.collect(model)


__all__ = ["mro_collect_table_spec"]
