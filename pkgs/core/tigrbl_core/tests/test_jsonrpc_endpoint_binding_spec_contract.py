from __future__ import annotations

import pytest


@pytest.mark.skip(reason="transport-dispatch governance placeholder until endpoint-keyed JSON-RPC bindings are implemented")
def test_http_jsonrpc_binding_spec_exposes_endpoint_identity() -> None:
    raise AssertionError("placeholder")
