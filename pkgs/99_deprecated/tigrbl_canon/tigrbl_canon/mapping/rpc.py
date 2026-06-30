from __future__ import annotations

from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)


from warnings import warn

from tigrbl_base._base._rpc_map import register_and_attach
from tigrbl_concrete._mapping.router.rpc import rpc_call

warn(
    "tigrbl_canon.mapping.rpc is deprecated; use tigrbl_base._base._rpc_map "
    "for register_and_attach and tigrbl_concrete._mapping.router.rpc for rpc_call",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["register_and_attach", "rpc_call"]
