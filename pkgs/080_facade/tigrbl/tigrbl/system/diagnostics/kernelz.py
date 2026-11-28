from __future__ import annotations

from typing import Any

from tigrbl_concrete.system.diagnostics.kernelz import (
    build_kernelz_endpoint as _build_kernelz_endpoint,
)
from tigrbl_kernel import _default_kernel


def build_kernelz_endpoint(router: Any):
    return _build_kernelz_endpoint(router, kernel=_default_kernel)


__all__ = ["build_kernelz_endpoint"]
