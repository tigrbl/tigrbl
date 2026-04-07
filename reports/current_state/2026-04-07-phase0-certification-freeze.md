# Current State Report

Date: 2026-04-07

## Summary

The repository now has a root-owned authoritative certification tree under `certification/`.

That tree separates the frozen certified release `0.3.18` from the active next-target line `0.3.19.dev1` using four explicit states:

- current
- target
- blocked
- evidenced

## What is certifiable now

Within the declared frozen `0.3.18` boundary, the package remains evidenced and current for:

- OpenAPI and JSON Schema emission
- JSON-RPC and OpenRPC surfaces
- retained RFC 7235, RFC 7617, and RFC 6750 rows
- closed operator surfaces
- closed CLI surface
- Gate A through Gate E release evidence

## What is not certifiable now

The active `0.3.19.dev1` line is not a promoted certified release.

It is not honestly describable as certifiably fully featured or certifiably fully RFC compliant because the datatype/table next-target program remains target- or blocked-state work.

## Phase 0 exit criteria status

- every next-target feature has owner, package, crate, test class, and claim target: yes
- every public claim has a certified-boundary flag: yes
- every risk has a mitigation owner: yes
- every issue is linked to a phase or waived explicitly: yes
