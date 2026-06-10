from __future__ import annotations

from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)


from warnings import warn

from tigrbl_concrete._mapping.router.resource_proxy import _ResourceProxy

warn(
    "tigrbl_canon.mapping.router.resource_proxy is deprecated; use tigrbl_concrete._mapping.router.resource_proxy",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["_ResourceProxy"]
