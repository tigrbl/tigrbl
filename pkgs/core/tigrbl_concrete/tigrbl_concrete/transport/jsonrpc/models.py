from __future__ import annotations

from tigrbl_concrete.schema.jsonrpc import *  # noqa: F401,F403
from tigrbl_concrete.transport._deprecation import (
    JSONRPC_MODELS_WARNING,
    warn_deprecated_transport_module,
)

warn_deprecated_transport_module(JSONRPC_MODELS_WARNING, __name__)
