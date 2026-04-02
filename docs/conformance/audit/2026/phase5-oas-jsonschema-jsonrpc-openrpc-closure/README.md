# Phase 5 OAS / JSON Schema / JSON-RPC / OpenRPC Closure Audit

This directory records the evidence captured for the Phase 5 checkpoint.

## Scope of this checkpoint

This phase closed the retained core docs/spec surfaces that were already partially present in the repository:

- OpenAPI 3.1.0 emission
- explicit JSON Schema Draft 2020-12 declaration via `jsonSchemaDialect`
- `components.schemas`, request body / response / parameter emission
- operation security emission from `secdeps`
- mounted `/openapi.json` and Swagger UI
- HTTP Basic added and aligned with the existing OAS security-scheme surface
- JSON-RPC 2.0 / OpenRPC 1.2.6 runtime/docs alignment
- mounted `/openrpc.json` and Lens / OpenRPC UI

This phase did **not** close the broader Phase 6 RFC/OIDC rows, the remaining missing docs UI rows, the operator-surface gaps, or the unified CLI.

## Runtime fix carried in this checkpoint

The request-time runtime compile failure that had previously broken mounted docs and JSON-RPC request paths is no longer present in this checkpoint.

The concrete fix ensures a resolved kernel is always present in:

- `pkgs/core/tigrbl_runtime/tigrbl_runtime/runtime/runtime.py`

## Snapshot artifacts

The generated snapshot artifacts for this checkpoint live under `snapshots/`:

- `openapi_snapshot.json`
- `openrpc_snapshot.json`
- `swagger_snapshot.html`
- `lens_snapshot.html`
- `snapshot_manifest.json`

## Targeted conformance suite result

The targeted Phase 5 suite recorded in `phase5_targeted_pytest.log` passed as:

- 59 passed
- 3 warnings

## Validator results on the final clean tree

- `validate_package_layout.py` — passed
- `validate_doc_pointers.py` — passed
- `validate_root_clutter.py` — passed
- `lint_claim_language.py` — passed
- `validate_boundary_freeze_manifest.py` — passed
- `lint_release_note_claims.py` — passed

## Evidence files

- `generate_phase5_snapshots.log`
- `phase5_targeted_pytest.log`
- `validate_package_layout.log`
- `validate_doc_pointers.log`
- `validate_root_clutter.log`
- `lint_claim_language.log`
- `validate_boundary_freeze_manifest.log`
- `lint_release_note_claims.log`
