# ASGI transport identity consumption conformance

Planned verification scenario.

Exercise runtime ingress with the canonical extension, the supported legacy projection, and a server without the extension.

1. Verify canonical fields reach HTTP, WebSocket, and WT dispatch. Preserve the distinction between the opening exchange and independently dispatched realtime requests. Keep requester session identity separate.
2. Exercise legacy fallback, an absent server connection ID, and contradictory identity inputs. Verify declared diagnostics and fallback behavior.
3. Through Tigrcorn, interleave streams and datagrams across two WT sessions on one QUIC connection. Verify that the projected connection ID is shared, transport session and WT correlation IDs differ between sessions, and each stream keeps its own correlation.
4. Inspect exported invocation and transport events for stable drillback through dispatch and cross-session delivery.

## Executable suite targets

- Add `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_asgi_transport_identity_consumption.py`.
- Extend `pkgs/97_tests/tigrbl_tests/tests/i9n/test_webtransport_tigrcorn_session_multiplexing.py`.
- Extend `pkgs/40_atoms/tigrbl_atoms/tests/test_webtransport_record_framing.py`.
- Extend `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_trace_qlog_contract.py`.

## Acceptance cases

- Drive canonical v1, legacy, absent, and contradictory scope inputs through ASGI ingress. Assert expected diagnostics, request ID inheritance or local allocation, and no synthesized server connection identity. Keep requester application session identity separate.
- Verify that an opening HTTP exchange ID remains attributable to the WS or WT handshake while later realtime requests and decoded invocations have their own appropriate identity.
- In the live Tigrcorn suite, prove that two WT sessions on one QUIC connection share the projected connection ID and have distinct transport-session and WT correlation IDs. Check per-stream correlation, interleaved datagrams, and continued operation of the other session after close.
- Reuse fragmented and coalesced record fixtures and assert invocation allocation at complete-message dispatch. Inspect exported records for connection, session, stream, and invocation drillback.

## Evidence required

Link the executable cases when they land. Keep this test planned until an actual run exercises the listed assertions and produces fresh evidence for the linked claim.
