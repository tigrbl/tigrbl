from __future__ import annotations

from pathlib import Path

import tigrbl_base._base._headers_base as headers_base_module
from tigrbl_base._base._response_base import ResponseBase
from tigrbl_core._spec.headers_spec import HeadersSpec


def test_response_base_serializes_headers_spec_as_plain_header_map() -> None:
    response = ResponseBase(headers=HeadersSpec(values={"X-Trace": "abc"}))

    assert response.headers["x-trace"] == "abc"
    assert response.raw_headers == [(b"x-trace", b"abc")]
    assert response.to_dict()["headers"] == {"x-trace": "abc"}


def test_headers_base_has_no_concrete_runtime_dependency() -> None:
    source = Path(headers_base_module.__file__).read_text(encoding="utf-8")

    assert "tigrbl_concrete" not in source
