from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    ExposurePolicyError,
    exposed_surfaces,
    resolve_exposure_policy,
)


HTTP_REST = {"kind": "http.rest", "path": "/items", "methods": ("GET",)}
JSONRPC = {"kind": "http.jsonrpc", "rpc_method": "Item.read"}


def test_docs_exposure_does_not_mount_runtime_transport():
    decision = resolve_exposure_policy(docs_exposure="default", runtime_exposure="none")

    assert decision.docs is True
    assert decision.runtime is False
    assert exposed_surfaces(decision) == ("openapi", "openrpc")


def test_runtime_exposure_does_not_publish_docs():
    decision = resolve_exposure_policy(
        docs_exposure="none",
        runtime_exposure="enabled",
        binding=HTTP_REST,
    )

    assert decision.docs is False
    assert decision.runtime is True
    assert exposed_surfaces(decision, HTTP_REST) == ("http",)


def test_docs_and_runtime_exposure_can_be_enabled_together_explicitly():
    decision = resolve_exposure_policy(
        docs_exposure="enabled",
        runtime_exposure="enabled",
        binding=JSONRPC,
    )

    assert exposed_surfaces(decision, JSONRPC) == ("openapi", "openrpc", "jsonrpc")


def test_docs_and_runtime_exposure_can_be_disabled_together():
    decision = resolve_exposure_policy(docs_exposure="none", runtime_exposure="none")

    assert exposed_surfaces(decision) == ()


def test_openapi_exposure_uses_docs_policy_not_runtime_policy():
    decision = resolve_exposure_policy(docs_exposure="enabled", runtime_exposure="none")

    assert "openapi" in exposed_surfaces(decision)


def test_openrpc_exposure_uses_docs_policy_not_runtime_policy():
    decision = resolve_exposure_policy(docs_exposure="enabled", runtime_exposure="none")

    assert "openrpc" in exposed_surfaces(decision)


def test_asgi_runtime_projection_uses_runtime_policy_not_table_class():
    decision = resolve_exposure_policy(
        docs_exposure="none",
        runtime_exposure="enabled",
        binding={"kind": "webtransport", "profile": "bidi_stream"},
    )

    assert exposed_surfaces(decision, {"kind": "webtransport"}) == ("webtransport",)


def test_runtime_exposure_requires_declared_transport_binding():
    with pytest.raises(ExposurePolicyError, match="requires declared transport binding"):
        resolve_exposure_policy(runtime_exposure="enabled")


def test_docs_exposure_for_unsupported_binding_fails_closed():
    with pytest.raises(ExposurePolicyError, match="unsupported transport binding"):
        resolve_exposure_policy(docs_exposure="enabled", binding={"kind": "local.memory"})


def test_runtime_exposure_for_unsupported_binding_fails_closed():
    with pytest.raises(ExposurePolicyError, match="unsupported transport binding"):
        resolve_exposure_policy(runtime_exposure="enabled", binding={"kind": "local.memory"})


def test_exposure_policy_reports_docs_and_runtime_sources():
    decision = resolve_exposure_policy(
        docs_exposure="enabled",
        runtime_exposure="enabled",
        binding=HTTP_REST,
    )

    assert decision.docs_source == "enabled"
    assert decision.runtime_source == "enabled"


def test_exposure_policy_output_is_deterministic():
    first = resolve_exposure_policy(
        docs_exposure="enabled",
        runtime_exposure="enabled",
        binding=HTTP_REST,
    )
    second = resolve_exposure_policy(
        docs_exposure="enabled",
        runtime_exposure="enabled",
        binding=HTTP_REST,
    )

    assert first == second
