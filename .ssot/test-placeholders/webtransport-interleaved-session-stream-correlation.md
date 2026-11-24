# WebTransport correlation under interleaved streams and datagrams

Planned conformance scenario.

Exercise two accepted WebTransport sessions on one underlying QUIC connection. Interleave two streams and a datagram in the first session with work on the second. Verify that all events in each session have its own correlation ID, the first session’s streams have distinct stable stream correlation IDs, and datagrams have no stream fields. Fragment a JSON-RPC record across reads and deliver several complete records in one read. Check that only complete records receive an invocation ID, each has its own ID, and originating context survives queued execution and reply or fan-out.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_webtransport_tigrcorn_session_multiplexing.py`
- `pkgs/45_kernel/tigrbl_kernel/tests/test_webtransport_session_plan.py`
- `pkgs/40_atoms/tigrbl_atoms/tests/test_webtransport_record_framing.py`

Use the Tigrcorn integration suite for session and lane identity. Assert invocation allocation through the control-loop dispatch path. Reuse the codec fixtures for fragmented and coalesced input.
