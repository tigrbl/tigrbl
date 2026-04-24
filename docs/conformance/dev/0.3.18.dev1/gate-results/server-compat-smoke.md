# Server Compatibility Smoke Lane

This lane covers supported-server smoke at the current checkpoint quality level.

## Current meaning

The current server-compatibility lane verifies runner dispatch and governed flag/config translation for:

- Uvicorn
- Hypercorn
- Gunicorn
- Tigrcorn

It does **not** yet claim full live-network or clean-room installed-package compatibility certification.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py`

## Source audit logs

- `docs/conformance/audit/2026/p8-cli/p8_cli_pytest.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_server_compat.log`
