from __future__ import annotations

import importlib
import sys
import warnings


def _fresh_import(module: str):
    sys.modules.pop(module, None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        imported = importlib.import_module(module)
    return imported, [warning for warning in caught if warning.category is DeprecationWarning]


def test_tigrbl_transport_rest_deprecation_warning() -> None:
    _, caught = _fresh_import("tigrbl.transport.rest.aggregator")

    messages = [str(warning.message) for warning in caught]
    assert any("tigrbl.transport.rest.aggregator is deprecated" in msg for msg in messages)
    assert any("not used by the Tigrbl runtime hot path" in msg for msg in messages)
    assert any("TigrblApp/TigrblRouter mounting APIs" in msg for msg in messages)


def test_tigrbl_transport_jsonrpc_model_deprecation_warning() -> None:
    _, caught = _fresh_import("tigrbl.transport.jsonrpc.models")

    messages = [str(warning.message) for warning in caught]
    assert any("tigrbl.transport.jsonrpc.models is deprecated" in msg for msg in messages)
    assert any("tigrbl.schema.jsonrpc" in msg for msg in messages)
    assert any("tigrbl_atoms.atoms.framing codecs" in msg for msg in messages)


def test_tigrbl_transport_jsonrpc_helper_deprecation_warning() -> None:
    _, caught = _fresh_import("tigrbl.transport.jsonrpc.helpers")

    messages = [str(warning.message) for warning in caught]
    assert any("tigrbl.transport.jsonrpc.helpers is deprecated" in msg for msg in messages)
    assert any("encode_frame/decode_frame" in msg for msg in messages)
    assert any("framing='jsonrpc'" in msg for msg in messages)


def test_tigrbl_concrete_transport_deprecation_warnings() -> None:
    modules = {
        "tigrbl_concrete.transport.rest.aggregator": "TigrblApp/TigrblRouter",
        "tigrbl_concrete.transport.jsonrpc.models": "tigrbl_concrete.schema.jsonrpc",
        "tigrbl_concrete.transport.jsonrpc.helpers": "encode_frame/decode_frame",
    }

    for module, replacement in modules.items():
        _, caught = _fresh_import(module)
        messages = [str(warning.message) for warning in caught]
        assert any(f"{module} is deprecated" in msg for msg in messages)
        assert any(replacement in msg for msg in messages)
