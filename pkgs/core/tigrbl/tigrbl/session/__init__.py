"""Compatibility exports for legacy ``tigrbl.session`` imports."""

from __future__ import annotations

from tigrbl_base._base import TigrblSessionBase
from tigrbl_core._spec.session_spec import SessionSpec

__all__ = ["SessionSpec", "TigrblSessionBase"]
