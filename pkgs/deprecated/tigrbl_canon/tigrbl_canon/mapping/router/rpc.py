from __future__ import annotations

from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)


from warnings import warn

from tigrbl_concrete._mapping.router.rpc import rpc_call

warn(
    "tigrbl_canon.mapping.router.rpc is deprecated; use tigrbl_concrete._mapping.router.rpc",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["rpc_call"]
