from __future__ import annotations

import pytest

from tigrbl_spec import (
    CURRENT_SCHEMA_VERSION,
    SpecSchemaError,
    SpecValidationError,
    UnsupportedSchemaVersionError,
    validate_payload,
)
from .helpers import app_payload


def test_valid_payload_identity_passes_validation() -> None:
    payload = app_payload()

    assert validate_payload("AppSpec", payload)["spec_schema_version"] == CURRENT_SCHEMA_VERSION


@pytest.mark.parametrize(
    ("field", "value", "error_type", "match"),
    [
        ("spec_kind", "ColumnSpec", SpecValidationError, "spec_kind"),
        ("spec_schema_version", "0.3.19", UnsupportedSchemaVersionError, "0.3.19"),
        ("spec_type", f"urn:tigrbl:spec:AppSpec:0.3.19", SpecValidationError, "spec_type"),
    ],
)
def test_wrong_identity_fields_fail_validation(
    field: str,
    value: str,
    error_type: type[SpecSchemaError],
    match: str,
) -> None:
    payload = app_payload()
    payload[field] = value

    with pytest.raises(error_type, match=match):
        validate_payload("AppSpec", payload)
