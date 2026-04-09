# Phase 6 Tigrcorn Hardening and Negative Certification Checkpoint

Date: 2026-04-09
Scope: next-target `0.3.19.dev1`
Checkpoint type: hardening contracts and negative-certification package

## What changed

The repo now publishes a Phase 6 hardening package for Tigrcorn-facing operation:

- five blessed deployment profiles
- machine-readable profile documents
- profile-specific negative corpus manifests
- profile-specific certification reports
- frozen proxy, early-data, and origin/pathsend/static contracts
- QUIC observability guidance with stable counters and explicitly experimental qlog-like export

The public CLI surface now exposes profile/contract controls through:

- `--deployment-profile`
- `--proxy-contract`
- `--early-data-policy`
- `--origin-static-policy`
- `--quic-metrics`
- `--qlog-dir`

## Boundary truth

This repository still does not contain a Tigrcorn implementation layer. The Phase 6 deliverable here is therefore a governed operator/control/certification boundary around an external runtime dependency.

That matters because it allows safe-failure policy and negative-certification posture to be documented and frozen without overstating framework ownership of Tigrcorn transport internals.

## Current truth

The active `0.3.19.dev1` line is still not certifiably fully featured.

The active `0.3.19.dev1` line is still not certifiably fully RFC compliant.
