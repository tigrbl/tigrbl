# Release Notes

This directory is the governed entry point for human-readable release notes.

## Claim rule

Every release-note file in this directory must declare:

- `Supported claim ids: <CLAIM_ID,...>`

The IDs must resolve to rows in `docs/conformance/CLAIM_REGISTRY.md` whose status is not:

- `not achieved`
- `missing`
- `partial`
- `deferred`
- `OOB`

If a release-note file uses Tier 3+ wording such as `certified`, `conformant`, `fully compliant`, or `fully featured`, every referenced claim must be Tier 3 or Tier 4.

## Current release note location

The current stable release note is published at:

- `docs/conformance/releases/0.3.18/RELEASE_NOTES.md`

Historical or supplemental release-note views may be added here later, but the governed stable release bundle remains the source of truth for the promoted current release.
