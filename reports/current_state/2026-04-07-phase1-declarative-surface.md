# Current State Report

Date: 2026-04-07

## Phase 1 status

The declarative and public Tigrbl surface has been extended in the workspace with:

- `Exchange`, `TxScope`, and `Framing` literals
- `OpSpec.exchange` and `OpSpec.tx_scope`
- direct binding declaration through `op_ctx(...)`
- direct selector declaration through `hook_ctx(...)`
- `security_deps` compatibility alongside `secdeps`
- `HttpStreamBindingSpec`
- `SseBindingSpec`
- `WebTransportBindingSpec`
- `WsBindingSpec(..., framing="jsonrpc")`
- alias decorators `websocket_ctx`, `sse_ctx`, `stream_ctx`, and `webtransport_ctx`
- docs-surface metadata sourced from declared bindings rather than handwritten approximations

## Current repository truth

This checkpoint improves the active `0.3.19.dev1` line, but it does not promote a new certified release.

The frozen `0.3.18` boundary remains the only line that is evidenced as certifiably fully featured and certifiably fully RFC/spec compliant within its declared boundary.

The active `0.3.19.dev1` line is still not honestly describable as certifiably fully featured or certifiably fully RFC compliant.

## Verification performed

- syntax verification via `py_compile` for edited source and test files
- policy validation via `python tools/ci/validate_phase1_declared_surface.py`

## Verification not performed

- full pytest execution was not possible in this environment because `pytest` is unavailable
- import-level runtime verification was incomplete because required dependencies such as `typing_extensions` are unavailable in this environment
