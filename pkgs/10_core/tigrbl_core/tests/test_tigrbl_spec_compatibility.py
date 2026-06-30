from __future__ import annotations

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core.schema import build_spec_json_schema_bundle
from tigrbl_spec import CURRENT_SCHEMA_VERSION, with_identity


def test_tigrbl_core_schema_imports_resolve_to_tigrbl_spec_catalog() -> None:
    bundle = build_spec_json_schema_bundle()

    assert bundle["authority"] == "tigrbl_spec"
    assert bundle["catalog_version"] == CURRENT_SCHEMA_VERSION


def test_tigrbl_core_spec_payloads_can_serialize_with_identity_fields() -> None:
    payload = with_identity("AppSpec", AppSpec().to_dict())

    assert payload["spec_kind"] == "AppSpec"
    assert payload["spec_schema_version"] == CURRENT_SCHEMA_VERSION
    assert payload["spec_type"] == f"urn:tigrbl:spec:AppSpec:{CURRENT_SCHEMA_VERSION}"
