"""Compatibility wrapper for canonical runtime event anchors.

Canonical event anchors and ordering now live in ``tigrbl_atoms.events``.
"""

from tigrbl_atoms.events import *  # noqa: F403
from tigrbl_atoms.events import __all__ as _ATOM_EVENT_EXPORTS
from tigrbl_atoms.events import canonicalize_phase


def is_error_phase(name: str) -> bool:
    phase = canonicalize_phase(name)
    return str(phase).startswith("ON_") or phase == "TX_ROLLBACK"


__all__ = [*_ATOM_EVENT_EXPORTS, "is_error_phase"]
