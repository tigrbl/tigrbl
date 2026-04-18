from __future__ import annotations

import pytest


@pytest.mark.skip(reason="transport-dispatch governance placeholder until REST/JSON-RPC parity is restored through the shared dispatch path")
def test_rest_and_jsonrpc_semantic_parity_survives_binding_materialization() -> None:
    raise AssertionError("placeholder")
