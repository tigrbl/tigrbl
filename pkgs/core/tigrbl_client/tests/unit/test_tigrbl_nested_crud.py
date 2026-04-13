from __future__ import annotations

import httpx

from tigrbl_client import TigrblClient


def test_nested_path_builds_hierarchical_resource_path() -> None:
    client = TigrblClient("http://example.com/api")
    assert client.nested_path("users", 1, "posts", 2) == "/users/1/posts/2"


def test_nested_collection_path_requires_parent_pairs() -> None:
    client = TigrblClient("http://example.com/api")
    try:
        client.nested_collection_path("users", resource="posts")
    except ValueError as exc:
        assert "resource/id pairs" in str(exc)
    else:
        raise AssertionError("Expected nested_collection_path() to validate parent pairs")


def test_nested_get_uses_underlying_crud_path(monkeypatch) -> None:
    captured: dict[str, str] = {}

    class DummyResponse:
        status_code = 200
        content = b"{}"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"ok": "yes"}

    def fake_get(self, url, params=None, headers=None):
        _ = params, headers
        captured["url"] = url
        return DummyResponse()

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    client = TigrblClient("http://example.com/api")
    result = client.nested_get("users", 1, "posts", 2)
    assert result == {"ok": "yes"}
    assert captured["url"] == "http://example.com/api/users/1/posts/2"
