# Security / Negative Lane

This lane covers retained HTTP auth behavior, security negative tests, and challenge/header semantics.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/security/test_schemes.py`
- `tools/ci/tests/test_http_auth_challenges.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_authorize_runtime_secdep.py`

## Source audit logs

- `docs/conformance/audit/2026/p6-rfc-sec/test_http_auth_challenges.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_security_negative.log`

- `docs/conformance/audit/2026/p11-gate-c/pytest_gate_c_conformance_security.log`
