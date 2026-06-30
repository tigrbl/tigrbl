from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl import APIKey
from tigrbl.security import Depends, Security
from tigrbl_concrete._concrete.dependencies import Dependency
from tigrbl_typing.status.exceptions import HTTPException


def _dep() -> str:
    return "ok"


def test_depends_and_security_preserve_callable_identity() -> None:
    depends = Depends(_dep)
    security = Security(_dep)

    assert isinstance(depends, Dependency)
    assert isinstance(security, Dependency)
    assert depends.dependency is _dep
    assert security.dependency is _dep


@pytest.mark.parametrize("factory", (Depends, Security))
def test_dependency_helpers_reject_non_callable_targets(factory) -> None:
    with pytest.raises(TypeError, match="callable"):
        factory("not-callable")


def test_api_key_header_query_cookie_resolution_and_auto_error() -> None:
    header_key = APIKey(name="X-API-Key", in_="header")
    query_key = APIKey(name="api_key", in_="query")
    cookie_key = APIKey(name="session", in_="cookie")

    assert (
        header_key(SimpleNamespace(headers={"x-api-key": "h"}, query_params={}))
        == "h"
    )
    assert (
        query_key(SimpleNamespace(headers={}, query_params={"api_key": "q"}))
        == "q"
    )
    assert (
        cookie_key(
            SimpleNamespace(headers={"cookie": "other=1; session=c"}, query_params={})
        )
        == "c"
    )

    with pytest.raises(HTTPException) as exc:
        header_key(SimpleNamespace(headers={}, query_params={}))
    assert exc.value.status_code == 403
    assert exc.value.detail == "Forbidden"


def test_api_key_openapi_projection_is_runtime_aligned() -> None:
    dependency = APIKey(
        scheme_name="QueryKey",
        name="api_key",
        in_="query",
        description="tenant API key",
        scopes=("items:read",),
    )

    assert dependency.openapi_security_scheme() == {
        "type": "apiKey",
        "name": "api_key",
        "in": "query",
        "description": "tenant API key",
    }
    assert dependency.openapi_security_requirement() == {"QueryKey": ["items:read"]}


def test_api_key_auto_error_false_does_not_leak_internal_details() -> None:
    dependency = APIKey(auto_error=False)

    assert dependency(SimpleNamespace(headers={}, query_params={})) is None
