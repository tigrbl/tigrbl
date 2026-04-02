# Phase 8 CLI Closure Evidence

This directory records the evidence captured for the Phase 8 unified CLI checkpoint.

## What this checkpoint closed

The Phase 8 checkpoint closes the last remaining current-target surface gap by adding the unified `tigrbl` CLI.

Closed in this checkpoint:

- `tigrbl run`
- `tigrbl serve`
- `tigrbl dev`
- `tigrbl routes`
- `tigrbl openapi`
- `tigrbl openrpc`
- `tigrbl doctor`
- `tigrbl capabilities`
- required CLI flags:
  - `--server {tigrcorn,uvicorn,hypercorn,gunicorn}`
  - `--host`
  - `--port`
  - `--reload`
  - `--workers`
  - `--root-path`
  - `--proxy-headers`
  - `--uds`
  - `--docs-path`
  - `--openapi-path`
  - `--openrpc-path`
  - `--lens-path`

## Important evidence interpretation

The supported-server smoke in this checkpoint is **runner-dispatch and configuration-translation smoke**. It verifies that the CLI translates its governed flags and dispatches correctly to the Uvicorn, Hypercorn, Gunicorn, and Tigrcorn runners.

It does **not** yet claim full installed-package, live-network, or clean-room server compatibility certification. That belongs to the later evidence, reproducibility, and promotion gates.

## Evidence artifacts

### CLI pytest slice

- `p8_cli_pytest.log`

Result summary:

- `14 passed`

### Governance / policy carry-forward pytest slice

- `policy_pytest.log`

Result summary:

- `9 passed`

### Policy validator logs

- `validate_package_layout.log`
- `validate_doc_pointers.log`
- `validate_root_clutter.log`
- `lint_claim_language.log`
- `validate_path_lengths.log`
- `validate_boundary_freeze_manifest.log`
- `lint_release_note_claims.log`

### Docs snapshots

- `docs-snapshots/CURRENT_TARGET.p8.md`
- `docs-snapshots/CURRENT_STATE.p8.md`
- `docs-snapshots/CLAIM_REGISTRY.p8.md`
- `docs-snapshots/IMPLEMENTATION_MAP.p8.md`
- `docs-snapshots/CLI_REFERENCE.p8.md`

## Final checkpoint position

After this checkpoint:

- there are no unresolved current-target surface gaps left in the governed docs tree
- Gate B can be treated as passed at checkpoint quality
- Tier 3 certification is still **not** achieved
- the remaining work is the later evidence-lane, reproducibility, and promotion program
