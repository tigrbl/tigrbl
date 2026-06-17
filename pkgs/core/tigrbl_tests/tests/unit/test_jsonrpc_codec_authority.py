from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest


CORE_ROOT = Path(__file__).resolve().parents[3]
CODEC_PATH = (
    CORE_ROOT
    / "tigrbl_atoms"
    / "tigrbl_atoms"
    / "atoms"
    / "framing"
    / "codec.py"
)
DEPRECATED_TRANSPORT_MODULE_PREFIXES = (
    "tigrbl.transport",
    "tigrbl_concrete.transport",
)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_jsonrpc_frame_codec_does_not_import_deprecated_transport_modules() -> None:
    imports = _imported_modules(CODEC_PATH)

    assert not {
        module
        for module in imports
        if module.startswith(DEPRECATED_TRANSPORT_MODULE_PREFIXES)
    }
    assert "tigrbl_concrete.schema.jsonrpc" not in imports
    assert "tigrbl.schema.jsonrpc" not in imports


def test_jsonrpc_frame_codec_runtime_does_not_load_transport_shims() -> None:
    for module_name in tuple(sys.modules):
        if module_name.startswith(DEPRECATED_TRANSPORT_MODULE_PREFIXES):
            sys.modules.pop(module_name)

    from tigrbl_atoms.atoms.framing.codec import decode_frame, encode_frame

    encoded = encode_frame(
        "jsonrpc",
        {"method": "items.list", "params": {"limit": 2}, "id": "req-1"},
    )

    assert encoded == (
        b'{"method":"items.list","params":{"limit":2},"id":"req-1","jsonrpc":"2.0"}'
    )
    assert decode_frame("jsonrpc", encoded) == {
        "method": "items.list",
        "params": {"limit": 2},
        "id": "req-1",
        "jsonrpc": "2.0",
    }
    assert not {
        module_name
        for module_name in sys.modules
        if module_name.startswith(DEPRECATED_TRANSPORT_MODULE_PREFIXES)
    }


def test_jsonrpc_frame_codec_is_authoritative_for_wire_validation() -> None:
    from tigrbl_atoms.atoms.framing.codec import decode_frame, encode_frame

    with pytest.raises(ValueError, match="invalid jsonrpc"):
        decode_frame("jsonrpc", json.dumps({"method": "items.list"}).encode("utf-8"))
    with pytest.raises(ValueError, match="invalid jsonrpc"):
        encode_frame(
            "jsonrpc",
            {"id": 1, "result": [], "error": {"code": -32600, "message": "bad"}},
        )
