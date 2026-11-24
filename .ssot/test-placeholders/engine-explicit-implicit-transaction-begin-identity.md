# Engine transaction identity on explicit and implicit begin

Planned conformance scenario.

Run against each supported transaction-capable engine adapter. Exercise explicit begin, provider autobegin including reads where applicable, and reuse of one engine session after commit or rollback. Assert exactly one fresh transaction ID per actual begin even when the wrapper and provider both observe it. Joining the active transaction reuses the ID. Rejected begin without an opened transaction creates no lifecycle ID. Verify that a failed commit does not establish a rollback and that unresolved outcomes retain the original identity.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_runtime_execution_contract.py`
- `pkgs/90_engines/tigrbl_engine_sqlite/tests/test_sqlite_session_batch_execution.py`
- `pkgs/90_engines/tigrbl_engine_postgres/tests/test_postgres_session_batch_execution.py`

Make the shared runtime contract executable and run the same identity contract against real SQLite and Postgres sessions first. Extend it to each supported transaction-capable adapter and provider mode. Exercise provider autobegin through normal reads and writes where applicable.
