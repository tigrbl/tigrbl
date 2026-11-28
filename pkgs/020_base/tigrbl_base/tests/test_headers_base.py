from tigrbl_core._spec.headers_spec import HeadersSpec
from tigrbl_base._base._headers_base import HeaderCookiesBase, HeadersBase


def test_headers_base_types() -> None:
    headers = HeadersBase({"content-type": "application/json"})
    cookies = HeaderCookiesBase({"sid": "abc"})

    assert isinstance(headers, dict)
    assert headers["content-type"] == "application/json"
    assert isinstance(cookies, dict)
    assert cookies["sid"] == "abc"


def test_headers_base_normalizes_mapping_and_pair_inputs() -> None:
    headers = HeadersBase([("Content-Type", "application/json"), (b"X-Trace", b"abc")])

    assert headers["content-type"] == "application/json"
    assert headers["CONTENT-TYPE"] == "application/json"
    assert "x-trace" in headers
    assert headers.get("X-Trace") == "abc"
    assert headers.raw_headers == [
        (b"content-type", b"application/json"),
        (b"x-trace", b"abc"),
    ]


def test_headers_base_accepts_headers_spec_and_projects_back_to_spec() -> None:
    spec = HeadersSpec(
        values={"X-Trace": "abc"},
        required=("X-Trace",),
        expose=("X-Trace",),
    )

    headers = HeadersBase(spec)
    restored = headers.as_spec()

    assert headers["x-trace"] == "abc"
    assert headers.required == ("x-trace",)
    assert headers.expose == ("x-trace",)
    assert restored == spec
