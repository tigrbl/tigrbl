from __future__ import annotations

import pytest

from tigrbl_spec import SpecValidationError, validate_payload, with_identity
from .helpers import headers_payload


def test_headers_spec_payload_validates_as_own_catalog_kind() -> None:
    payload = headers_payload()

    assert validate_payload("HeadersSpec", payload) == payload


def test_headers_spec_rejects_non_string_header_values() -> None:
    payload = headers_payload()
    payload["values"]["x-trace"] = 42

    with pytest.raises(SpecValidationError, match="values.x-trace"):
        validate_payload("HeadersSpec", payload)


def test_request_and_response_headers_remain_plain_string_maps() -> None:
    request = with_identity(
        "RequestSpec",
        {
            "method": "GET",
            "path": "/widgets",
            "headers": {"x-token": "abc"},
            "query": {"page": ["1"]},
            "path_params": {},
            "body": "",
            "script_name": "",
            "app": None,
        },
    )
    response = with_identity(
        "ResponseSpec",
        {
            "kind": "json",
            "media_type": "application/json",
            "status_code": 200,
            "headers": {"x-trace": "abc"},
            "envelope": None,
            "template": None,
            "filename": None,
            "download": None,
            "etag": None,
            "cache_control": None,
            "redirect_to": None,
        },
    )

    assert validate_payload("RequestSpec", request)["headers"] == {"x-token": "abc"}
    assert validate_payload("ResponseSpec", response)["headers"] == {"x-trace": "abc"}


def test_request_headers_do_not_accept_nested_headers_spec_payload() -> None:
    request = with_identity(
        "RequestSpec",
        {
            "method": "GET",
            "path": "/widgets",
            "headers": headers_payload(),
            "query": {},
            "path_params": {},
            "body": "",
            "script_name": "",
            "app": None,
        },
    )

    with pytest.raises(SpecValidationError, match=r"headers\."):
        validate_payload("RequestSpec", request)
