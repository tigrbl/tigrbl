# Gate C Conformance Security

This gate-result file records the dedicated Gate C proof added by the Gate C conformance/security checkpoint.

## Source validator

- `tools/ci/validate_gate_c_conformance_security.py`

## Source workflow

- `.github/workflows/gate-c-conformance-security.yml`

## Source tests

- `pkgs/core/tigrbl_tests/tests/unit/test_spec_snapshots.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openapi_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_swagger_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openrpc_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_lens_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/security/test_schemes.py`
- `tools/ci/tests/test_http_auth_challenges.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_authorize_runtime_secdep.py`
- `tools/ci/tests/test_gate_c_conformance_security.py`

## Source audit logs

- `docs/conformance/audit/2026/p11-gate-c/validate_gate_c_conformance_security.log`
- `docs/conformance/audit/2026/p11-gate-c/pytest_gate_c_conformance_security.log`
- `docs/conformance/audit/2026/p11-gate-c/pytest_governance_and_gate_c.log`
