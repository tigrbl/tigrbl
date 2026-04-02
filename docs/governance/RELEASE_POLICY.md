# Release Policy

## Release classes

### Development checkpoints

Development checkpoints:

- use `0.x.y.devN`
- may contain partial current-target closure
- may not use certification wording

### Stable releases

Stable releases:

- use `0.x.y`
- require synchronized docs, claims, and evidence
- require reproducible release artifacts
- may use certification wording only if Tier 3 evidence is met within boundary

## Required release artifacts

Stable releases should publish:

- release notes
- claims document
- evidence index
- current target snapshot
- gate results
- artifact manifest

## Release-note claim rule

Feature, spec, security, or certification claims in release notes must be governed.

Each release-note file under `docs/release-notes/` or `docs/conformance/releases/` must declare:

- `Supported claim ids: <CLAIM_ID,...>`

The referenced claim IDs must exist in `docs/conformance/CLAIM_REGISTRY.md` and may not point at rows whose status is:

- `not achieved`
- `missing`
- `partial`
- `deferred`
- `OOB`

If a release note uses Tier 3+ certification wording, every referenced claim must also be Tier 3 or Tier 4.
