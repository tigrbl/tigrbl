"""tigrbl_engine_inmemory package."""

from .rust import register_rust_engine
from .plugin import register

__all__ = ["register", "register_rust_engine", "__version__"]
__version__ = "0.1.0"
