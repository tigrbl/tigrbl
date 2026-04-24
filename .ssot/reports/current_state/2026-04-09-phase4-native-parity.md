# Phase 4 Native Parity Checkpoint

Date: 2026-04-09

## Scope completed in this checkpoint

- mirrored more of the Python transport/spec vocabulary into Rust with
  `Exchange`, `TxScope`, richer `OpSpec`, richer `BindingSpec`, and hook
  selector metadata;
- added route/opview/phase-plan parity snapshots on the native side and a
  matching Python reference artifact contract;
- added differential Python-vs-native parity suites for snapshots and transport
  traces;
- added packed-plan parity checks in both Python-facing and Rust-native tests;
- added REST, JSON-RPC, SSE, WS/WSS, and WebTransport transport traces to the
  parity contract surface;
- added a fail-closed policy validator so native backend claims are blocked
  until the parity lanes are wired and evidenced.

## Verification produced in this checkpoint

- `py_compile` passed for the touched Python native/kernel/runtime wrappers and
  the Phase 4 validator.
- Python smoke passed for the native parity snapshot and transport trace helpers
  in source-fallback mode.
- `cargo test -p tigrbl_rs_spec --test spec_contract -- --nocapture` passed
  with the new Rust transport/spec literals.
- `cargo test -p tigrbl_rs_kernel --test kernel_contract --test parity_contract -- --nocapture`
  passed.
- `cargo test -p tigrbl_rs_runtime --test runtime_contract --test parity_contract -- --nocapture`
  passed.

## State still not claimable as certified release truth

This checkpoint does **not** justify claiming that the active `0.3.19.dev1` line is certifiably fully featured or certifiably fully RFC/spec compliant.

It also does **not** justify claiming that the native backend is now fully
claimable. The repo now has route/opview/phase-plan parity snapshots,
differential Python-vs-native parity suites, packed-plan parity, and
REST, JSON-RPC, SSE, WS/WSS, and WebTransport transport traces, but these are
still parity-contract lanes rather than full release-grade execution parity.

The remaining gaps are:

- the Python-native bridge is still source-fallback oriented in this workspace;
- full end-to-end behavior parity against the real compiled native backend was
  not produced here for hooks, errors, docs generation, and every live
  transport path;
- the parity lanes were implemented and exercised as checkpoint proof, not yet
  as complete release evidence for native certification claims.
