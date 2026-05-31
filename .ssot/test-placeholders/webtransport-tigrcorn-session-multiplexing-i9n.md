# Planned Test: WebTransport Tigrcorn Session Multiplexing Integration

This planned test will be replaced by `pkgs/core/tigrbl_tests/tests/i9n/test_webtransport_tigrcorn_session_multiplexing.py` when the runtime proof is implemented.

Required coverage:

- one WebTransport scope and one session id
- at least two bidirectional streams
- one client-to-server unidirectional stream
- one server-to-client unidirectional stream
- at least two datagrams
- all events preserve session and lane identity
- no native WebTransport message lane
