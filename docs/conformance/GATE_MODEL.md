# Gate Model

## Current position

Gate A remains passed for the current cycle.

The closed current-target release bundle is established by named gate, surface, evidence, and promotion checkpoints; post-promotion handoff establishes the release-history split.

What is now true:

- the current-target cycle still has a machine-checked freeze marker and manifest
- path-length governance is enforced alongside layout/pointer/root-clutter/claim-language checks
- the retained RFC/security rows are narrower and more explicit than they were before the RFC/security boundary review
- the docs/operator surface boundary is explicit and closed for this cycle
- the CLI boundary is explicit and closed for this cycle
- Gate B is passed at checkpoint quality and machine-checked in CI
- Gate C is passed at checkpoint quality and machine-checked in CI
- Gate D is passed at checkpoint quality and machine-checked in CI
- Gate E is passed in the Gate E promotion checkpoint and machine-checked in CI
- the certification program has explicit lane classes, a machine-readable evidence registry, governed dev/release bundle roots, explicit gate result artifacts, and a promoted stable release bundle
- the package has Tier 3 current-boundary certification status for stable release `0.3.18`
- Post-promotion handoff freezes `0.3.18` as release history and opens governed next-target planning on `0.3.19.dev1`

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

## Release-decision map

For certification-bundle lifecycle and release-decision reporting, the repo also preserves the following explicit A-E interpretation:

- Gate A: surface freeze
- Gate B: correctness
- Gate C: interop
- Gate D: performance/operability
- Gate E: security/abuse

This mapping is preserved in the certification bundle so release decisions are machine-checkable without implying undeclared RFC or feature scope.

See `gates/` for the per-gate condition documents. Post-promotion handoff is a post-promotion handoff checkpoint rather than a new certification gate.
