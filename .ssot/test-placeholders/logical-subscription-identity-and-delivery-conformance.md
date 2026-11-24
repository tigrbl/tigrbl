# Logical subscription identity and delivery conformance

Planned verification scenario.

Exercise the realtime broker through both WebSocket and WebTransport bindings.

1. Admit subscriptions on distinct channels on one carrier under the existing channel policy. Verify distinct logical IDs and compatibility of binding-selected acknowledgement versions. V2 carries the logical ID separately from destination transport identity.
2. Resume an admitted subscription across reconnect. Assert the logical ID is stable, the new attachment is active, and stale cleanup from the old carrier leaves it active. Verify lease-generation fencing and quota accounting.
3. Publish to multiple recipients. Assert a unique delivery per recipient and preserved publication, subscription, origin invocation, destination correlation, and actual outcome.
4. Verify failed or refused admission omits a successful subscription acknowledgement. Verify unsubscribe and current-carrier disconnect release the correct attachment.
5. Export and roll up the resumed subscription history. Count the logical subscription once and preserve drillback to both destinations and their deliveries.

## Executable suite targets

- Add `pkgs/97_tests/tigrbl_tests/tests/i9n/test_logical_subscription_identity_lifecycle.py`.
- Extend `pkgs/60_ops/tigrbl_ops_realtime/tests/test_broker.py`.
- Extend `pkgs/60_ops/tigrbl_ops_realtime/tests/test_quotas.py`.
- Extend `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_trace_qlog_contract.py`.
- Extend `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_runtime_rollup_contract.py`.

## Acceptance cases

- Drive both WS and WT through normal bindings. Assert v1 compatibility and v2 logical subscription identity, including distinct subscriptions under the current channel policy and no successful acknowledgement after refusal.
- Run a controlled resume-versus-old-carrier-cleanup race with a deterministic handoff. Verify stable logical identity, current attachment and generation, quota counts, and cleanup of the correct attachment on unsubscribe or current-carrier close.
- Publish to multiple recipients and verify one delivery per recipient with publication, subscription, origin invocation, recipient correlation, and actual outcome.
- Replace relevant skipped export and rollup assertions with executable cases. Verify a single logical subscription across both destinations and drillback through each publication and delivery. Include a shared transaction fixture to prove transaction counts remain deduplicated by engine session and transaction ID.

## Evidence required

Link the executable cases when they land. Keep this test planned until an actual run exercises the listed assertions and produces fresh evidence for the linked claim.
