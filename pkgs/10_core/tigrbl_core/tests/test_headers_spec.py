from __future__ import annotations

import tigrbl_core._spec as spec
from tigrbl_core._spec.headers_spec import HeadersSpec
from tigrbl_core._spec.serde import SerdeMixin


def test_headers_spec_normalizes_collection_fields() -> None:
    headers = HeadersSpec(
        values={"Content-Type": "application/json", b"X-Trace": b"abc"},
        required=("Content-Type",),
        expose=("X-Trace",),
    )

    assert headers.values == {
        "content-type": "application/json",
        "x-trace": "abc",
    }
    assert headers.required == ("content-type",)
    assert headers.expose == ("x-trace",)
    assert headers.get("CONTENT-TYPE") == "application/json"


def test_headers_spec_serde_round_trip() -> None:
    headers = HeadersSpec(
        values={"X-Trace": "abc"},
        required=("X-Trace",),
        expose=("X-Trace",),
    )

    restored = HeadersSpec.from_json(headers.to_json())

    assert isinstance(headers, SerdeMixin)
    assert restored == HeadersSpec(
        values={"x-trace": "abc"},
        required=("x-trace",),
        expose=("x-trace",),
    )


def test_headers_spec_is_exported_from_core() -> None:
    assert spec.HeadersSpec is HeadersSpec
    assert "HeadersSpec" in spec.__all__
