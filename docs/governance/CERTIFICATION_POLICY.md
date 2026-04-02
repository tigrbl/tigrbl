# Certification Policy

## Purpose

Certification language is controlled. This repository may only use certification wording when the documented claim tier permits it.

## Boundary rule

Certification applies only within the declared current target boundary. Server/runtime transport ownership remains outside the framework claim set unless explicitly added later.

## Claim language rule

The following wording is reserved for Tier 3+ evidence quality:

- certified
- conformant
- fully compliant
- fully featured

Below Tier 3, use implementation or planning language only.

## Evidence rule

A claim is not certifiable until:

- the boundary is frozen
- the claim is listed in the claim registry
- required tests and evidence exist
- docs, code, and evidence agree
- the applicable gates have passed

## Gate A rule

The current-target cycle is frozen for this checkpoint. Changes to the frozen boundary documents require synchronized updates to:

- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`
- `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`

## Current checkpoint status

The promoted stable release `0.3.18` satisfies the governed Gate A through Gate E sequence for the Tier 3 current-boundary claim rows in `docs/conformance/CLAIM_REGISTRY.md`.

The active `0.3.19.dev1` line is a next-target planning checkpoint and does **not** use Tier 3 certification wording.
