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

## Linux CI investigation

The focused suite reproduced the [Gate E failures](https://github.com/tigrbl/tigrbl/actions/runs/42429009109) on Linux with Python 3.12.13, SQLite 3.46.1, and the locked development dependencies. It reported four failures, three passes, nine expected failures, and two teardown errors. On Windows the same focused suite reported seven passes and nine expected failures.

- REST and HTTP JSON-RPC reported successful `clear` and `bulk_delete` operations, but the deleted rows remained. The SQL trace showed a prior read session rolling back on the shared in-memory SQLite connection between the delete and its commit.
- Malformed IDs returned HTTP 500 and JSON-RPC error `-32603`. The Linux pytest runner timed out while cancelling pending session-close tasks during teardown.
- A test-only experiment awaited the session-close tasks scheduled by each HTTP request. All four deletion assertions passed, and the two teardown timeouts cleared. The run still reported nine expected failures for scalar HTTP write persistence, malformed-ID error mapping, and WebSocket bulk write persistence.
- A separate filtered-clear probe inserted one matching row and one nonmatching row. Both transports deleted both rows. The clear handler passed empty filters to the persistence operation, and the SQL trace showed a delete without a `WHERE` clause.

## Runtime fixes and focused verification

- The request executors await async session cleanup before returning. The Linux run completed without the teardown timeouts or lost deletes.
- Storage assembly writes to hydrated instances and preserves ORM descriptors on the table class. Scalar HTTP updates and replaces and WebSocket bulk updates, replaces, and merges now persist in the transport tests.
- Selector validation applies the declared ULID pattern and length before persistence. Malformed IDs return client errors, while well-formed missing IDs keep their existing not-found responses.
- Filtered clear preserves nonmatching rows and rejects unsupported filters. The REST and HTTP JSON-RPC tests verify both outcomes.

The focused suite passed on Linux and Windows with 103 passes and five existing skips per platform, including all 16 transport cases. Issue #43 stays open.

## Clear and WebSocket error regressions

- REST, HTTP JSON-RPC, and WebSocket JSON-RPC reject malformed clear filters before deleting any rows. REST also rejects invalid JSON and non-object bodies. A valid filter preserves nonmatching rows, and an omitted filter still clears the collection.
- WebSocket JSON-RPC returns `-32602` for malformed ULIDs and `-32003` for well-formed IDs that do not identify a row, matching HTTP JSON-RPC.
