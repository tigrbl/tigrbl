# Phase 5 Tigrcorn Operator Surface Checkpoint

Date: 2026-04-09
Scope: next-target `0.3.19.dev1`
Checkpoint type: public operator/config surface closure

## What changed

The repo now exposes a governed Tigrcorn operator surface through the public `tigrbl` CLI and diagnostic payloads.

The Phase 5 checkpoint covers:

- StatsD / DogStatsD export controls
- OpenTelemetry / tracing export controls
- graceful drain and shutdown timeout controls
- concurrency limiting / admission control
- backlog tuning
- WebSocket keepalive / heartbeat controls
- HTTP/2 tuning
- richer HTTP/3 / QUIC tuning
- ALPN policy control
- OCSP / revocation policy control
- release-gated interop artifact bundle directories
- formal benchmark / throughput artifact bundle directories

The public surface is implemented in `pkgs/core/tigrbl/tigrbl/cli.py`, reflected in `tigrbl doctor`, and discoverable via `tigrbl capabilities`.

## Public examples and docs

Repo-owned example configs now exist at:

- `docs/developer/examples/tigrcorn/phase5-operator-config.json`
- `docs/developer/examples/tigrcorn/phase5-interop-bundle-manifest.json`
- `docs/developer/examples/tigrcorn/phase5-benchmark-bundle-manifest.json`

The operator controls are documented in `docs/developer/CLI_REFERENCE.md`.

## What this does not prove

This checkpoint does **not** prove that the repository is certifiably fully featured or certifiably fully RFC compliant.

It also does **not** prove that Tigrcorn transport/runtime behavior itself is framework-owned. In this repository, Tigrcorn remains an external serving/runtime layer reached through a governed CLI adapter surface.

Live interop bundles and formal benchmark / throughput artifacts remain release-gated evidence lanes rather than completed certification evidence in this workspace.

## Checkpoint evidence

- CLI/server translation smoke covers the new Tigrcorn operator flags
- `doctor` output now emits operator_controls derived from the real declared CLI surface
- repo-owned docs/examples/validator/workflow pointers keep the surface freezeable in policy CI

## Current truth

The active `0.3.19.dev1` line is still not certifiably fully featured.

The active `0.3.19.dev1` line is still not certifiably fully RFC compliant.
