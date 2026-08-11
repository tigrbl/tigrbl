from .dedupe import DedupeSet
from .engine import DedupeEngine
from .plugin import build_memdedupe, register
from .session import AsyncDedupeSession, DedupeSession

__all__ = [
    "AsyncDedupeSession",
    "DedupeEngine",
    "DedupeSession",
    "DedupeSet",
    "__version__",
    "build_memdedupe",
    "register",
]
__version__ = "0.4.5.dev4"
