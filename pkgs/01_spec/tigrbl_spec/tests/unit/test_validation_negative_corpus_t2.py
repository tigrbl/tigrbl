from __future__ import annotations

import pytest

from tigrbl_spec import (
    SpecValidationError,
    UnknownSpecKindError,
    UnsupportedSchemaVersionError,
    validate_payload,
)
from .helpers import app_payload, binding_payload


def test_negative_corpus_rejects_missing_identity() -> None:
    payload = app_payload()
    payload.pop("spec_kind")

    with pytest.raises(SpecValidationError, match="spec_kind"):
        validate_payload("AppSpec", payload)


def test_negative_corpus_rejects_wrong_urn() -> None:
    payload = app_payload()
    payload["spec_type"] = "urn:tigrbl:spec:ColumnSpec:0.3.20"

    with pytest.raises(SpecValidationError, match="spec_type"):
        validate_payload("AppSpec", payload)


def test_negative_corpus_rejects_unknown_kind() -> None:
    payload = app_payload()

    with pytest.raises(UnknownSpecKindError, match="UnknownSpec"):
        validate_payload("UnknownSpec", payload)


def test_negative_corpus_rejects_unsupported_version() -> None:
    payload = app_payload()
    payload["spec_schema_version"] = "0.3.19"

    with pytest.raises(UnsupportedSchemaVersionError, match="0.3.19"):
        validate_payload("AppSpec", payload)


def test_negative_corpus_rejects_nested_ref_shape_failures() -> None:
    payload = binding_payload()
    payload["spec"] = {"proto": "http.rest"}

    with pytest.raises(SpecValidationError, match="BindingSpec payload"):
        validate_payload("BindingSpec", payload)
