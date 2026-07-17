"""Read-only memory engine for Tigrbl."""

from .engine import ROMEngine
from .plugin import build_rom, capabilities, register
from .session import READ_ONLY_ERROR, ROMResult, ROMSession

__all__ = [
    "READ_ONLY_ERROR",
    "ROMEngine",
    "ROMResult",
    "ROMSession",
    "build_rom",
    "capabilities",
    "register",
    "__version__",
]

__version__ = "0.4.5.dev4"
