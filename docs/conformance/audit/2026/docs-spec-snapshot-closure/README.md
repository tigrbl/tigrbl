# Docs Spec Snapshot Closure

This audit artifact stores generated OpenAPI, OpenRPC, Swagger, and Lens snapshots for docs/spec conformance checks.

## Generated Artifacts

- `snapshots/openapi_snapshot.json`
- `snapshots/openrpc_snapshot.json`
- `snapshots/swagger_snapshot.html`
- `snapshots/lens_snapshot.html`
- `snapshot_manifest.json`

## Regeneration

Run `python tools/conformance/generate_spec_snapshots.py` from the repository root with the workspace packages on `PYTHONPATH`.
