# WebSocket correlation through asynchronous dispatch and fan-out

Planned conformance scenario for SPEC-1147 and SPEC-2208.

Run plain application-message and JSON-RPC bindings through the normal socket dispatch path. Interleave two logical requests on the same socket. Hold the first queued invocation until the second completes, then emit a reply or fan-out to another socket. Verify distinct request correlation IDs, a fresh invocation ID for each decoded message, continuity for a multi-message request, and origin attribution on delayed work. Assert that the recipient retains its receiving transport session identity. For JSON-RPC preserve the wire ID independently of invocation identity.

## Executable targets

- `pkgs/45_kernel/tigrbl_kernel/tests/test_websocket_jsonrpc_session.py`
- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_websocket_batch_scheduler.py`
