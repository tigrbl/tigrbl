# Runtime rollup and visualization drillback by correlation

Planned conformance scenario for SPEC-1125, SPEC-2177, and SPEC-2208.

Consume an exported trace fixture containing two WebTransport sessions on one QUIC connection, several streams, a datagram, two invocations sharing an engine transaction, and a retry that starts another transaction. Query the session correlation, then stream correlation, invocation, and transaction links. Verify that the datagram appears at the session level, the second session can be selected independently, all participant links survive aggregation, and each engine session and transaction pair contributes only one begin and one outcome. Run the query after compaction to verify drillback survives.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_runtime_rollup_contract.py`
