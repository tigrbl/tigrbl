"""Deprecated names for the ZDoc documentation viewer."""

from __future__ import annotations

from typing import Any
from warnings import warn

from .zdoc import build_zdoc_html, mount_zdoc


def build_lens_html(router: Any, request: Any, *, spec_path: str) -> str:
    warn("build_lens is deprecated. Use build_zdoc instead.", DeprecationWarning, stacklevel=2)
    return build_zdoc_html(router, request, spec_path=spec_path)


def mount_lens(
    router: Any, *, path: str = "/lens", name: str = "__lens__",
    spec_path: str | None = None, openrpc_url: str | None = None, title: str | None = None,
) -> Any:
    warn("mount_lens is deprecated. Use mount_zdoc instead.", DeprecationWarning, stacklevel=2)
    return mount_zdoc(router, path=path, name=name, spec_path=spec_path or openrpc_url, title=title)


__all__ = ["build_lens_html", "mount_lens"]
