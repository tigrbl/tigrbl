from __future__ import annotations

import warnings
from typing import NoReturn


RUST_DEPRECATION_MESSAGE = (
    "Tigrbl Rust runtime support is deprecated and unavailable; "
    "Tigrbl runtime execution is Python-only. Use executor_backend='python'."
)


class RustSupportDeprecatedError(RuntimeError):
    """Raised when deprecated Rust support is requested."""


class RustBindingsUnavailableError(RustSupportDeprecatedError):
    """Raised when the deprecated Rust runtime binding surface is requested."""


def warn_rust_deprecated(*, stacklevel: int = 2) -> None:
    warnings.warn(RUST_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=stacklevel)


def raise_rust_deprecated(action: str) -> NoReturn:
    warn_rust_deprecated(stacklevel=3)
    raise RustBindingsUnavailableError(f"{action} is unavailable. {RUST_DEPRECATION_MESSAGE}")
