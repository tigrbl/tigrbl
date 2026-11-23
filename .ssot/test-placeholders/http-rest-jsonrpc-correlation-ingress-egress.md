# HTTP REST and JSON-RPC ingress and egress correlation

Planned conformance scenario for SPEC-2105 and SPEC-2208.

Exercise the normal ASGI entry point. Verify that a valid ID from a trusted upstream is returned as X-Correlation-ID, and that absent, invalid, or untrusted values result in a generated ID. Assert the same header on REST success, malformed bodies, route or authorization errors, and HTTP JSON-RPC notification-only responses. On HTTP JSON-RPC, send a batch with a successful request, an error, and a notification. Verify one request correlation ID and one document invocation ID, a distinct zero-based rpc_item_index per dispatched item, unchanged rpc_id for responses, and no response object for notifications. Reuse a wire RPC ID in an independent request and prove the invocation IDs differ.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_http_rest_jsonrpc_atom_chain_contract.py`
- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_jsonrpc_batch_behavior.py`
