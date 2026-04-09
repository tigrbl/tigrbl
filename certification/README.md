# Certification Authority

This tree is the authoritative certification boundary and truth model for the repository.

It separates:

- frozen current-boundary claims
- active next-target claims
- blocked closure items
- evidence-backed claims

See `certification/boundary.yaml`.

Machine validation is enforced by `tools/ci/validate_certification_tree.py`.
