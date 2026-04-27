from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl import HTTPBearer
from tigrbl.runtime.status import HTTPException


def test_httpbearer_missing_credentials_raise_401_bearer_challenge() -> None:
    dependency = HTTPBearer(realm="api")
    request = SimpleNamespace(headers={})

    with pytest.raises(HTTPException) as exc_info:
        dependency(request)

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.detail == "Not authenticated"
    assert exc.headers["WWW-Authenticate"] == 'Bearer, realm="api"'


def test_httpbearer_malformed_header_uses_invalid_request_challenge() -> None:
    dependency = HTTPBearer()
    request = SimpleNamespace(headers={"authorization": "Bearer"})

    with pytest.raises(HTTPException) as exc_info:
        dependency(request)

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.headers["WWW-Authenticate"] == 'Bearer, error="invalid_request"'


def test_httpbearer_auto_error_false_returns_none_for_missing_or_bad_header() -> None:
    dependency = HTTPBearer(auto_error=False)

    assert dependency(SimpleNamespace(headers={})) is None
    assert dependency(SimpleNamespace(headers={"authorization": "Basic abc"})) is None
    assert dependency(SimpleNamespace(headers={"authorization": "Bearer   "})) is None

