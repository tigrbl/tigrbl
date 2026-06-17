from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace

from tigrbl_concrete._concrete._security.http_basic import HTTPBasic
from tigrbl_concrete._concrete._security.http_bearer import HTTPBearer
from tigrbl_typing.status.exceptions import HTTPException

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_http_basic_missing_header_emits_401_challenge() -> None:
    dep = HTTPBasic(realm='unit')
    try:
        dep(SimpleNamespace(headers={}))
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.headers == {'WWW-Authenticate': 'Basic realm="unit"'}
    else:  # pragma: no cover
        raise AssertionError('expected HTTPException')


def test_http_basic_invalid_header_emits_401_challenge() -> None:
    dep = HTTPBasic(realm='unit')
    try:
        dep(SimpleNamespace(headers={'authorization': 'Basic not-base64'}))
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.headers == {'WWW-Authenticate': 'Basic realm="unit"'}
    else:  # pragma: no cover
        raise AssertionError('expected HTTPException')


def test_http_bearer_missing_header_emits_401_challenge() -> None:
    dep = HTTPBearer(realm='unit')
    try:
        dep(SimpleNamespace(headers={}))
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.headers == {'WWW-Authenticate': 'Bearer, realm="unit"'}
    else:  # pragma: no cover
        raise AssertionError('expected HTTPException')


def test_http_bearer_wrong_scheme_emits_invalid_request_challenge() -> None:
    dep = HTTPBearer(realm='unit')
    try:
        dep(SimpleNamespace(headers={'authorization': 'Basic abc'}))
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.headers == {
            'WWW-Authenticate': 'Bearer, realm="unit", error="invalid_request"'
        }
    else:  # pragma: no cover
        raise AssertionError('expected HTTPException')


def test_http_basic_valid_credentials_decode() -> None:
    dep = HTTPBasic(realm='unit')
    token = base64.b64encode(b'alice:secret').decode('ascii')
    credentials = dep(SimpleNamespace(headers={'authorization': f'Basic {token}'}))
    assert credentials.username == 'alice'
    assert credentials.password == 'secret'


def test_http_bearer_valid_credentials_decode() -> None:
    dep = HTTPBearer(realm='unit')
    credentials = dep(SimpleNamespace(headers={'authorization': 'Bearer token-123'}))
    assert credentials.scheme == 'Bearer'
    assert credentials.credentials == 'token-123'


def test_executor_and_sender_source_preserve_http_exception_headers() -> None:
    packed_text = (
        REPO_ROOT / 'pkgs' / 'core' / 'tigrbl_runtime' / 'tigrbl_runtime' / 'executors' / 'packed.py'
    ).read_text(encoding='utf-8')
    asgi_send_text = (
        REPO_ROOT / 'pkgs' / 'core' / 'tigrbl_atoms' / 'tigrbl_atoms' / 'atoms' / 'egress' / 'asgi_send.py'
    ).read_text(encoding='utf-8')

    assert 'headers=getattr(exc, "headers", None)' in packed_text
    assert 'headers: Mapping[str, str] | None = None' in asgi_send_text
    assert 'for key, value in (headers or {}).items()' in asgi_send_text
