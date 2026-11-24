# Caller-owned transactions and transaction-free invocations

Planned conformance scenario for SPEC-2170 and SPEC-2208.

Begin a real transaction through an engine session and call an operation that joins it through the normal runtime entry point. Verify one engine begin, the existing engine-issued transaction ID, the invocation participation link, and no commit or rollback by the joining operation. Finish the transaction as its caller and verify the original ID on the outcome. Then run a transaction-free operation and assert that it assigns no transaction ID, emits no transaction lifecycle events, and records no transaction participation link.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_runtime_execution_contract.py`
- `pkgs/90_engines/tigrbl_engine_sqlite/tests/test_sqlite_session_batch_execution.py`
