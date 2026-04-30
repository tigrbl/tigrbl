from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def validate_webtransport_scope(scope: Mapping[str, Any]) -> Mapping[str, Any]:
    if str(scope.get("type")) != "webtransport":
        raise ValueError("webtransport scope metadata requires type='webtransport'")
    if not scope.get("path"):
        raise ValueError("webtransport scope metadata requires a path")
    quic = scope.get("quic") or {}
    if not isinstance(quic, Mapping) or not quic.get("alpn"):
        raise ValueError("webtransport scope metadata requires quic metadata with alpn")
    return scope


__all__ = ["validate_webtransport_scope"]
