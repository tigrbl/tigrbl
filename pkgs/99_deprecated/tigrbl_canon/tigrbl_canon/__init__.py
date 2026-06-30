"""Tigrbl canon compatibility package."""

from __future__ import annotations

import warnings

_DEPRECATION_MESSAGE = (
    "tigrbl_canon is deprecated, not supported anymore, and likely to break. "
    "Migrate away from tigrbl_canon imports as soon as possible."
)


def _warn_deprecated_import(module_name: str = __name__) -> None:
    message = (
        _DEPRECATION_MESSAGE
        if module_name == __name__
        else f"{module_name} imports from deprecated tigrbl_canon. {_DEPRECATION_MESSAGE}"
    )
    warnings.warn(message, DeprecationWarning, stacklevel=2)


_warn_deprecated_import()

__all__ = ["_DEPRECATION_MESSAGE", "_warn_deprecated_import"]
