from __future__ import annotations

import base64
import importlib.util
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from types import ModuleType, SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]


def _register_module(name: str, module: ModuleType) -> None:
    sys.modules[name] = module


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Minimal dependency stubs for direct module loading.
_previous_modules = {
    name: sys.modules.get(name)
    for name in [
        'tigrbl_runtime',
        'tigrbl_runtime.runtime',
        'tigrbl_runtime.runtime.status',
        'tigrbl_runtime.runtime.status.exceptions',
        'tigrbl_runtime.runtime.status.mappings',
        'tigrbl_base',
        'tigrbl_base._base',
        'tigrbl_base._base._security_base',
    ]
}

for package_name in [
    'tigrbl_runtime',
    'tigrbl_runtime.runtime',
    'tigrbl_runtime.runtime.status',
    'tigrbl_base',
    'tigrbl_base._base',
]:
    if package_name not in sys.modules:
        module = ModuleType(package_name)
        module.__path__ = []  # type: ignore[attr-defined]
        _register_module(package_name, module)

exc_module = ModuleType('tigrbl_runtime.runtime.status.exceptions')


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = '', headers: dict[str, str] | None = None) -> None:
        super().__init__(detail)
        self.status_code = int(status_code)
        self.detail = detail
        self.headers = dict(headers or {})


exc_module.HTTPException = HTTPException
_register_module('tigrbl_runtime.runtime.status.exceptions', exc_module)

map_module = ModuleType('tigrbl_runtime.runtime.status.mappings')
map_module.status = SimpleNamespace(HTTP_401_UNAUTHORIZED=401, HTTP_403_FORBIDDEN=403)
_register_module('tigrbl_runtime.runtime.status.mappings', map_module)

base_module = ModuleType('tigrbl_base._base._security_base')


class OpenAPISecurityDependency:
    def __init__(self, *, scheme_name: str, scheme: dict, scopes=None, auto_error: bool = True) -> None:
        self.scheme_name = scheme_name
        self.auto_error = auto_error
        self._scheme = dict(scheme)
        self._scopes = list(scopes or [])

    def openapi_security_scheme(self) -> dict:
        return dict(self._scheme)

    def openapi_security_requirement(self) -> dict[str, list[str]]:
        return {self.scheme_name: list(self._scopes)}


base_module.OpenAPISecurityDependency = OpenAPISecurityDependency
_register_module('tigrbl_base._base._security_base', base_module)

http_basic_module = _load_module(
    'http_basic',
    REPO_ROOT / 'pkgs' / 'core' / 'tigrbl_concrete' / 'tigrbl_concrete' / '_concrete' / '_security' / 'http_basic.py',
)
http_bearer_module = _load_module(
    'http_bearer',
    REPO_ROOT / 'pkgs' / 'core' / 'tigrbl_concrete' / 'tigrbl_concrete' / '_concrete' / '_security' / 'http_bearer.py',
)
HTTPBasic = http_basic_module.HTTPBasic
HTTPBearer = http_bearer_module.HTTPBearer

for _name, _module in _previous_modules.items():
    if _module is None:
        sys.modules.pop(_name, None)
    else:
        sys.modules[_name] = _module


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
