from __future__ import annotations

from tigrbl_concrete._concrete._request import Request, UploadedFile
from tigrbl_concrete._concrete._response import Response


def test_request_cookies_parse_multiple_cookie_values() -> None:
    request = Request(
        "GET",
        "/cookies",
        headers={"cookie": "sid=abc123; tenant=acme; theme=dark"},
    )

    assert request.cookies.sid == "abc123"
    assert request.cookies.tenant == "acme"
    assert request.cookies.get("theme") == "dark"
    assert request.cookies.get("missing") is None


def test_response_set_cookie_preserves_extended_cookie_attributes() -> None:
    response = Response.text("ok")

    response.set_cookie(
        "sid",
        "abc123",
        path="/auth",
        domain="example.com",
        secure=True,
        httponly=True,
        samesite="lax",
        max_age=120,
        expires="Wed, 09 Jun 2021 10:18:14 GMT",
    )

    set_cookie = response.headers_map["set-cookie"]
    assert "sid=abc123" in set_cookie
    assert "Path=/auth" in set_cookie
    assert "Domain=example.com" in set_cookie
    assert "Secure" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Max-Age=120" in set_cookie
    assert "expires=Wed, 09 Jun 2021 10:18:14 GMT" in set_cookie


def test_urlencoded_form_preserves_repeated_fields_as_lists() -> None:
    request = Request(
        "POST",
        "/form",
        headers={"content-type": "application/x-www-form-urlencoded"},
        body=b"name=alice&tag=one&tag=two&empty=",
    )

    assert request.form_sync() == {
        "name": "alice",
        "tag": ["one", "two"],
        "empty": "",
    }


def test_multipart_form_keeps_scalar_fields_and_uploaded_file_metadata() -> None:
    boundary = "aab03x"
    body = (
        b"--aab03x\r\n"
        b'Content-Disposition: form-data; name="title"\r\n\r\n'
        b"Quarterly Report\r\n"
        b"--aab03x\r\n"
        b'Content-Disposition: form-data; name="attachment"; filename="report.txt"\r\n'
        b"Content-Type: text/plain\r\n\r\n"
        b"hello-upload\r\n"
        b"--aab03x--\r\n"
    )
    request = Request(
        "POST",
        "/upload",
        headers={"content-type": f"multipart/form-data; boundary={boundary}"},
        body=body,
    )

    form = request.form_sync()
    file = request.files["attachment"]

    assert form["title"] == "Quarterly Report"
    assert isinstance(file, UploadedFile)
    assert file.filename == "report.txt"
    assert file.content_type == "text/plain"
    assert file.body == b"hello-upload"
    assert file.text() == "hello-upload"
    assert file.size == len(b"hello-upload")


def test_multipart_repeated_file_field_returns_file_list() -> None:
    body = (
        b"--boundary\r\n"
        b'Content-Disposition: form-data; name="files"; filename="a.txt"\r\n'
        b"Content-Type: text/plain\r\n\r\n"
        b"a\r\n"
        b"--boundary\r\n"
        b'Content-Disposition: form-data; name="files"; filename="b.txt"\r\n'
        b"Content-Type: text/plain\r\n\r\n"
        b"b\r\n"
        b"--boundary--\r\n"
    )
    request = Request(
        "POST",
        "/upload",
        headers={"content-type": "multipart/form-data; boundary=boundary"},
        body=body,
    )

    files = request.files["files"]

    assert isinstance(files, list)
    assert [file.filename for file in files] == ["a.txt", "b.txt"]
    assert [file.text() for file in files] == ["a", "b"]


def test_multipart_without_boundary_fails_closed_to_empty_form() -> None:
    request = Request(
        "POST",
        "/upload",
        headers={"content-type": "multipart/form-data"},
        body=b"not-a-parseable-body",
    )

    assert request.form_sync() == {}
    assert request.files == {}
