# Trace context and identity linkage in exported runtime records

Planned conformance scenario for SPEC-1103, SPEC-2178, and SPEC-2208.

Send a known valid HTTP trace context and verify the server span has the expected trace and parent span, alongside the independently assigned request correlation. Generate WebTransport session, stream, datagram, and invocation events, plus a transaction shared by two invocations. Exercise the declared runtime trace/qlog export path. Verify required fields by event kind, absence of stream fields on datagrams, separation of origin and recipient transport identity, and exactly one lifecycle record per transaction event with both participation links. Reject a stream belonging to another transport session or participation associated with the wrong engine session.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_trace_qlog_contract.py`
- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_webtransport_tigrcorn_session_multiplexing.py`
