# Certification Authority

This tree is the authoritative certification boundary and truth model for the repository.

It separates:

- frozen current-boundary claims
- active next-target claims
- blocked closure items
- evidence-backed claims

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

See `certification/boundary.yaml`.

Machine validation is enforced by `tools/ci/validate_certification_tree.py`.
