from __future__ import annotations

from warnings import warn


REST_WARNING = (
    "{module} is deprecated and retained only as a compatibility shim. "
    "It is not used by the Tigrbl runtime hot path and will be removed in a "
    "future release. Use TigrblApp/TigrblRouter mounting APIs or "
    "tigrbl_concrete model binding surfaces instead."
)

JSONRPC_MODELS_WARNING = (
    "{module} is deprecated and retained only as a compatibility shim. "
    "It is not used by the Tigrbl runtime hot path and will be removed in a "
    "future release. Use tigrbl.schema.jsonrpc or tigrbl_concrete.schema.jsonrpc; "
    "use tigrbl_atoms.atoms.framing codecs for runtime JSON-RPC payload validation."
)

JSONRPC_HELPERS_WARNING = (
    "{module} is deprecated and retained only as a compatibility shim. "
    "It is not used by the Tigrbl runtime hot path and will be removed in a "
    "future release. Use tigrbl_atoms.atoms.framing.encode_frame/decode_frame "
    "with framing='jsonrpc' for JSON-RPC envelopes."
)


def warn_deprecated_transport_module(message_template: str, module: str) -> None:
    warn(message_template.format(module=module), DeprecationWarning, stacklevel=3)


__all__ = [
    "JSONRPC_HELPERS_WARNING",
    "JSONRPC_MODELS_WARNING",
    "REST_WARNING",
    "warn_deprecated_transport_module",
]
