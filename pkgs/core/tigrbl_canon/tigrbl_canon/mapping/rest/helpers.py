from __future__ import annotations

from warnings import warn

from tigrbl_base._base._rest_map import (
    _Key,
    _coerce_parent_kw,
    _ensure_jsonable,
    _get_phase_chains,
    _pk_name,
    _pk_names,
    _req_state_db,
)

warn(
    "tigrbl_canon.mapping.rest.helpers is deprecated; use tigrbl_base._base._rest_map",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "_Key",
    "_coerce_parent_kw",
    "_ensure_jsonable",
    "_get_phase_chains",
    "_pk_name",
    "_pk_names",
    "_req_state_db",
]
