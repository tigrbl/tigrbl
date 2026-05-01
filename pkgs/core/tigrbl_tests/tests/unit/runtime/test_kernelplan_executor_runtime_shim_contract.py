from __future__ import annotations

import importlib
from pathlib import Path


_SHIM_EXPORTS = (
    ("tigrbl_runtime.protocol.http_unary", "run_http_rest_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.http_unary", "run_http_jsonrpc_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.http_stream", "run_http_stream_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.sse", "run_sse_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.websocket", "run_websocket_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.lifespan_chain", "run_lifespan_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.static_files", "run_static_file_chain", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.webtransport", "validate_webtransport_scope", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.transport_atoms", "run_transport_emit", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol.subevent_handlers", "dispatch_subevent", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol._iterators", "iter_items", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.protocol._iterators", "aclose_if_supported", "tigrbl_atoms.protocol_runtime"),
    ("tigrbl_runtime.callbacks", "register_callback", "tigrbl_atoms.runtime_callbacks"),
    ("tigrbl_runtime.callbacks", "run_callback_fence", "tigrbl_atoms.runtime_callbacks"),
    ("tigrbl_runtime.channel.state", "create_channel_state", "tigrbl_atoms.runtime_channel"),
    ("tigrbl_runtime.channel.state", "transition_channel_state", "tigrbl_atoms.runtime_channel"),
    ("tigrbl_runtime.transactions", "run_subevent_tx_unit", "tigrbl_atoms.runtime_transactions"),
)


def test_runtime_surfaces_delegate_to_atom_owned_implementations() -> None:
    for runtime_module_name, attr_name, atom_module_name in _SHIM_EXPORTS:
        runtime_module = importlib.import_module(runtime_module_name)
        atom_module = importlib.import_module(atom_module_name)
        assert getattr(runtime_module, attr_name) is getattr(atom_module, attr_name)


def test_packed_executor_source_avoids_runtime_shadow_compiler_helpers() -> None:
    packed_module = importlib.import_module("tigrbl_runtime.executors.packed")
    source = Path(packed_module.__file__).read_text(encoding="utf-8")

    forbidden = (
        "tigrbl_runtime.protocol.http_unary",
        "tigrbl_runtime.protocol.http_stream",
        "tigrbl_runtime.protocol.sse",
        "tigrbl_runtime.protocol.websocket",
        "tigrbl_runtime.protocol.lifespan_chain",
        "tigrbl_runtime.protocol.static_files",
        "tigrbl_runtime.protocol.transport_atoms",
        "tigrbl_runtime.protocol.subevent_handlers",
        "tigrbl_runtime.callbacks",
        "tigrbl_runtime.transactions",
    )

    assert all(name not in source for name in forbidden)
