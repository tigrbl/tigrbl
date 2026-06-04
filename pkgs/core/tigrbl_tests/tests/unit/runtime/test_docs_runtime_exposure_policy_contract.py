import pytest


pytestmark = pytest.mark.skip(
    reason="Docs/runtime exposure policy enforcement is not implemented yet."
)


def test_docs_exposure_does_not_mount_runtime_transport():
    raise NotImplementedError


def test_runtime_exposure_does_not_publish_docs():
    raise NotImplementedError


def test_docs_and_runtime_exposure_can_be_enabled_together_explicitly():
    raise NotImplementedError


def test_docs_and_runtime_exposure_can_be_disabled_together():
    raise NotImplementedError


def test_openapi_exposure_uses_docs_policy_not_runtime_policy():
    raise NotImplementedError


def test_openrpc_exposure_uses_docs_policy_not_runtime_policy():
    raise NotImplementedError


def test_asgi_runtime_projection_uses_runtime_policy_not_table_class():
    raise NotImplementedError


def test_runtime_exposure_requires_declared_transport_binding():
    raise NotImplementedError


def test_docs_exposure_for_unsupported_binding_fails_closed():
    raise NotImplementedError


def test_runtime_exposure_for_unsupported_binding_fails_closed():
    raise NotImplementedError


def test_exposure_policy_reports_docs_and_runtime_sources():
    raise NotImplementedError


def test_exposure_policy_output_is_deterministic():
    raise NotImplementedError
