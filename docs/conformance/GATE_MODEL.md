# Gate Model

## Current position

Gate A remains passed for the current cycle.

Checkpoints 5 through 13 establish the closed current-target release bundle, and Phase 14 establishes the post-promotion handoff.

What is now true:

- the current-target cycle still has a machine-checked freeze marker and manifest
- path-length governance is enforced alongside layout/pointer/root-clutter/claim-language checks
- the retained RFC/security rows are narrower and more explicit than they were before Phase 6
- the docs/operator surface boundary is explicit and closed for this cycle
- the CLI boundary is explicit and closed for this cycle
- Gate B is passed at checkpoint quality and machine-checked in CI
- Gate C is passed at checkpoint quality and machine-checked in CI
- Gate D is passed at checkpoint quality and machine-checked in CI
- Gate E is passed in the Phase 13 promotion checkpoint and machine-checked in CI
- the certification program has explicit lane classes, a machine-readable evidence registry, governed dev/release bundle roots, explicit gate result artifacts, and a promoted stable release bundle
- the package has Tier 3 current-boundary certification status for stable release `0.3.18`
- Phase 14 freezes `0.3.18` as release history and opens governed next-target planning on `0.3.19.dev1`

What is not yet true:

- Tier 4 external validation is not yet established
- the active `0.3.19.dev1` line is not yet a promoted or certified release
- the next-target datatype/table program is still planning work

## Gates

- Gate A — boundary freeze
- Gate B — surface closure
- Gate C — conformance and security closure
- Gate D — reproducibility and package assembly
- Gate E — promotion and release

See `gates/` for the per-gate condition documents. Phase 14 is a post-promotion handoff checkpoint rather than a new certification gate.
