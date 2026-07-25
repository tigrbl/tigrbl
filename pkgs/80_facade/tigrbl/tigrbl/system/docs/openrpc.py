"""Public facade for canonical OpenRPC document generation."""

from tigrbl_concrete.system.docs.openrpc import build_openrpc_spec, mount_openrpc

__all__ = ["build_openrpc_spec", "mount_openrpc"]
