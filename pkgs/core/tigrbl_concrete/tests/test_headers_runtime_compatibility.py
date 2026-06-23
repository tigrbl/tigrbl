from __future__ import annotations

from tigrbl_base._base._headers_base import HeadersBase
from tigrbl_concrete._concrete._headers import Headers
from tigrbl_concrete._concrete._response import Response
from tigrbl_core._spec.headers_spec import HeadersSpec


def test_concrete_headers_preserve_plain_mapping_compatibility() -> None:
    headers = Headers({"Content-Type": "application/json"})

    assert headers["content-type"] == "application/json"
    assert headers.get("CONTENT-TYPE") == "application/json"


def test_concrete_headers_accept_headers_spec() -> None:
    spec = HeadersSpec(values={"X-Trace": "abc"})

    headers = Headers(spec)

    assert headers["x-trace"] == "abc"
    assert headers.as_list() == [("x-trace", "abc")]


def test_response_accepts_headers_spec_without_changing_public_header_map() -> None:
    response = Response(headers=HeadersSpec(values={"X-Trace": "abc"}))

    assert response.headers["x-trace"] == "abc"
    assert response.headers_map["X-Trace"] == "abc"
    assert response.raw_headers == [(b"x-trace", b"abc")]


def test_response_accepts_headers_base() -> None:
    response = Response(headers=HeadersBase({"X-Trace": "abc"}))

    assert response.headers["x-trace"] == "abc"
    assert response.raw_headers == [(b"x-trace", b"abc")]
