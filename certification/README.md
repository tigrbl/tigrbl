# Certification Projections

`.ssot/registry.json` is the authoritative machine-readable source of truth for the repository, with authored policy documents under `.ssot/adr/` and `.ssot/specs/`.

This tree contains derived certification projections, gate inputs, and historical release bundles.

It separates:

- frozen current-boundary claims
- active next-target claims
- blocked closure items
- evidence-backed claims

The projection files `certification/claims/target.yaml` and `certification/targets/next_target.yaml` are deprecated and must not receive new source edits. New planning, feature, claim, and boundary work belongs in the SSOT.

For normalized tracking across features, claims, tests, and evidence, use the
generated universal registry artifact at
`certification/registries/universal_registry.json`.

That file is the consolidated machine-readable registry view consumed by the CSV
registry outputs:

- `certification/registries/feature_registry.csv`
- `certification/registries/claims_registry.csv`
- `certification/registries/test_registry.csv`
- `certification/registries/naming_conventions.csv`

Build and validate it with:

- `python tools/ci/build_universal_registry.py`
- `python tools/ci/generate_registry_csvs.py`
- `python tools/ci/validate_universal_registry.py`

See `certification/boundary.yaml` for the derived certification projection
entry point.

Machine validation is enforced by `tools/ci/validate_certification_tree.py`.
