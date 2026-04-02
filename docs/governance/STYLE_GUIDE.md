# Documentation Style Guide

## General rules

- write in precise, declarative language
- distinguish clearly between implemented, partial, missing, deferred, and out-of-boundary
- avoid promotional language for uncertified surfaces
- prefer explicit file paths and concrete surface names

## Claim wording

Use claim language that matches the current claim tier. Do not imply certification where the gate model and evidence do not support it.

Outside `docs/governance/`, `docs/conformance/`, and `docs/adr/`, do not use certification language such as:

- `certified`
- `certifiably`
- `conformant`
- `fully featured`
- `fully compliant`

Use neutral wording in package-local distribution READMEs and developer docs.

## Structure

Each governance or conformance document should state:

- what it governs
- current status
- boundaries or exclusions
- consequences for contributors or operators
