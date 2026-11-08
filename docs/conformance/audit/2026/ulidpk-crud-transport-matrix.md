# ULID primary key CRUD transport verification

GitHub issue #43. Local run on the proposed integration test and the existing REST, JSON-RPC, and ULID mixin suites.

| Binding | Result |
| --- | --- |
| REST and HTTP JSON-RPC | Standard, OLTP, and bulk operations dispatch with a ULID-backed table. Bulk writes persist and target the intended row. Scalar update and replace return the intended values but a later read can return the original values. Malformed member identifiers surface as internal errors. |
| WebSocket JSON-RPC | All 15 built-in operations dispatch through explicit bindings. Bulk update, replace, and merge return the intended values but a later read can return the original values. |
| HTTP streaming, SSE, and WebTransport | The built-in profiles declare stream and realtime operations. They have no built-in CRUD defaults to verify. |

Ruff format and lint passed for the new integration test. The combined pytest run reported 37 passed, 5 existing skips, and 9 strict expected failures. The expected failures reproduce scalar HTTP write persistence, WebSocket bulk write persistence, and malformed HTTP member handling. A control run using `GUIDPk` also reproduced scalar HTTP update and replace persistence failures.

```text
python -m pytest -q pkgs/97_tests/tigrbl_tests/tests/i9n/test_v3_default_rest_ops.py pkgs/97_tests/tigrbl_tests/tests/i9n/test_v3_default_rpc_ops.py pkgs/97_tests/tigrbl_tests/tests/i9n/test_ulidpk_crud_transports.py pkgs/97_tests/tigrbl_tests/tests/unit/test_ulidpk_mixin.py
```
