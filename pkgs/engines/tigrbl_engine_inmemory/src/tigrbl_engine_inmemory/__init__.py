"""tigrbl_engine_inmemory package."""

from .native import register_native_engine
from .plugin import register

__all__ = ["register", "register_native_engine", "__version__"]
__version__ = "0.1.0"
