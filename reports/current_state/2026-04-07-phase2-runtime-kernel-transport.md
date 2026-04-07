# Phase 2 Runtime/Kernel Transport Checkpoint

Date: 2026-04-07

## Scope completed in this checkpoint

- Added `OpChannel` and transport family/subevent typing to `tigrbl_typing`.
- Added runtime-owned ASGI channel adapters under `tigrbl_runtime/channel/`.
- Routed websocket scopes through runtime invocation instead of the direct
  concrete websocket bypass.
- Added runtime-owned completion tracking and a deterministic `POST_EMIT`
  marker after channel completion.
- Removed the Python runtime import dependency on `tigrbl_concrete`.
- Added Rust port/runtime channel mirrors in `tigrbl_rs_ports` and
  `tigrbl_rs_runtime`.
- Changed AsyncAPI generation to use declared transport bindings instead of the
  handwritten `websocket_routes` list.

## State still not claimable as certified release truth

This checkpoint does **not** justify claiming that the active `0.3.19.dev1`
line is certifiably fully featured or certifiably fully RFC/spec compliant.

The remaining gaps are:

- the runtime channel model is real and repo-owned, but the live loop model for
  every exchange/family is not yet complete across Python and Rust;
- `POST_EMIT` is deterministic as a runtime completion marker, but not yet a
  fully compiled and hookable phase across the kernel/runtime surface;
- WebTransport and stream-family execution remain adapter-backed rather than
  fully transport-specialized runtime loops;
- no full repository test/CI evidence was produced in this environment.
