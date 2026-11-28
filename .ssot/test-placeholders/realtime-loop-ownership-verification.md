# Realtime loop ownership verification

This plan covers SPEC-1147, SPEC-1153, SPEC-2108, SPEC-2159, and SPEC-2207. New test records point to this plan until their executable cases are implemented.

## New conformance cases

### WebTransport outer session-plan delegation

`tst:webtransport-outer-session-plan-delegation`

Enter through TigrblApp and observe one kernel session-plan entry per inbound ASGI scope. Interleave stream and datagram dispatch. End one stream, verify another lane still works, then disconnect and verify the terminal session admits no further work.

Intended executable targets

- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_asgi_scope_dispatch_delegation.py`

### WebTransport control-stream record lifecycle

`tst:webtransport-control-record-loop`

Exercise split length prefixes, split payloads, and multiple records in one read. Incomplete records dispatch nothing. Complete records dispatch once with distinct invocation IDs and correlated nonterminal replies. Verify ending the control stream leaves other lanes available.

Intended executable targets

- `pkgs/45_kernel/tigrbl_kernel/tests/test_webtransport_session_plan.py`
- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_webtransport_tigrcorn_session_multiplexing.py`

### Framework-managed realtime session termination and cleanup

`tst:realtime-session-terminal-cleanup`

For both managed transports, cover peer disconnect, cancellation, terminal receive failure, terminal send failure, and repeated or concurrent terminal signals. Assert one ordered cleanup sequence. Inject a failed cleanup effect, verify later independent effects run, and preserve the original failure or cancellation. Scope effects to the owning session and lane.

Intended executable targets

- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_realtime_session_terminal_cleanup.py`

## Extensions to existing coverage

- `tst:websocket-app-handler-does-not-own-loop-contract` Exercise both binding modes through public ASGI ingress. Observe direct kernel plan entry. A managed binding accepts once and dispatches complete messages once. An explicit app handler retains accept, receive, send, and close through the socket API. Apply the loop ownership restriction to framework-managed realtime bindings.
- `tst:websocket-session-close-cleanup-order-contract` Assert the exact pre-close, structural close, and post-close order. Verify peer disconnect still releases local state when the carrier can no longer send.
- `tst:logical-subscription-identity-and-delivery-conformance` Resume a subscription on a replacement carrier. Terminate the original session through the real cleanup path. Verify attachment generation fences the stale cleanup and subsequent deliveries reach the replacement carrier.
- `tst:webtransport-tigrcorn-session-multiplexing-i9n` Re-run the SPEC-2159 mixed-lane fixture through one kernel session-plan entry and verify identity across interleaved bidirectional, unidirectional, and datagram traffic.
- `tst:webtransport-tigrcorn-session-close-cascade-i9n` Drive session termination through the kernel-selected plan. Verify owned remaining lanes are cleaned up once and no new operation or lane admission follows termination.

For verification, confirm that routing a WebTransport event back through the outer session entry fails the single-entry assertion. Confirm that running cleanup twice fails the cleanup-attempt assertion.
