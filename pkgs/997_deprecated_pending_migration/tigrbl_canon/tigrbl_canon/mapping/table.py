from __future__ import annotations

from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)


from .model import bind, rebind

__all__ = ["bind", "rebind"]
