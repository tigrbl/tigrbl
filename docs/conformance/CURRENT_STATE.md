# Current State

## Status summary

This repository now has a governed documentation and policy baseline for Phase 0. The package is **not yet** at a Tier 3 certifiable state for “fully featured” or “fully RFC/spec/standard compliant” claims.

## Repository composition

- core Python packages: 15
- engine packages: 22
- app packages: 6
- Rust crates: 9
- Python binding packages: 1

### Core packages

- `tigrbl`
- `tigrbl_atoms`
- `tigrbl_base`
- `tigrbl_canon`
- `tigrbl_client`
- `tigrbl_concrete`
- `tigrbl_core`
- `tigrbl_kernel`
- `tigrbl_ops_olap`
- `tigrbl_ops_oltp`
- `tigrbl_orm`
- `tigrbl_runtime`
- `tigrbl_spec`
- `tigrbl_tests`
- `tigrbl_typing`

### Engine packages

- `tigrbl_engine_bigquery`
- `tigrbl_engine_clickhouse`
- `tigrbl_engine_csv`
- `tigrbl_engine_dataframe`
- `tigrbl_engine_duckdb`
- `tigrbl_engine_inmemcache`
- `tigrbl_engine_inmemory`
- `tigrbl_engine_membloom`
- `tigrbl_engine_memdedupe`
- `tigrbl_engine_memkv`
- `tigrbl_engine_memlru`
- `tigrbl_engine_mempubsub`
- `tigrbl_engine_memqueue`
- `tigrbl_engine_memrate`
- `tigrbl_engine_numpy`
- `tigrbl_engine_pandas`
- `tigrbl_engine_pgsqli_wal`
- `tigrbl_engine_pyspark`
- `tigrbl_engine_redis`
- `tigrbl_engine_rediscachethrough`
- `tigrbl_engine_snowflake`
- `tigrbl_engine_xlsx`

### App packages

- `tigrbl_acme_ca`
- `tigrbl_api_cron`
- `tigrbl_api_hpks`
- `tigrbl_billing`
- `tigrbl_kms`
- `tigrbl_spiffe`

### Rust crates

- `tigrbl_rs_atoms`
- `tigrbl_rs_engine_inmemory`
- `tigrbl_rs_engine_postgres`
- `tigrbl_rs_engine_sqlite`
- `tigrbl_rs_kernel`
- `tigrbl_rs_ops_oltp`
- `tigrbl_rs_ports`
- `tigrbl_rs_runtime`
- `tigrbl_rs_spec`

## Phase 0 work completed in this checkpoint

- preserved Apache 2.0 licensing already present in the supplied archive
- added contributor, conduct, and security policy files at the root
- created a governed docs tree for governance, conformance, ADRs, developer docs, and notes
- added canonical pointers from the root README to target, state, next steps, governance, contributing, conduct, and security docs
- archived legacy root-level status/build-proof materials into `docs/conformance/archive/2026/phase0-authority-reset/`
- removed generated `target/` output from the checkpoint zip

## Existing implemented surfaces observed from the supplied repository state

### OAS / docs / security

- OpenAPI document emission at `3.1.0`
- `info`, `paths`, request bodies, responses, path/query parameters
- `components.schemas`
- `components.securitySchemes`
- operation-level `security`
- `/openapi.json`
- Swagger UI
- OpenRPC JSON
- Lens / OpenRPC UI
- OAS security scheme surface for `apiKey`, `http`, `oauth2`, `openIdConnect`, and `mutualTLS`
- generic auth/security plumbing via `AuthNProvider`, router/app auth configuration, security dependencies, and `OpSpec.secdeps`

### Public framework surface observed

- REST
- JSON-RPC surface exists, though explicit JSON-RPC 2.0 closure remains partial
- request/response surface
- templating
- middleware protocol

### Rust-native additive checkpoint observed

The archived legacy current-state material shows an additive Rust-native substrate with:

- Rust crates under `crates/`
- Python bindings under `bindings/python/tigrbl_native`
- public backend-selection and boundary-trace surfaces
- crate-level Rust tests and selected Python native-surface tests
- a source-importable Python fallback for the native binding surface

See the archived legacy checkpoint materials for the exact older wording and build proof package.

## Partial current-target surfaces

- explicit JSON Schema Draft 2020-12 closure
- explicit JSON-RPC 2.0 target
- OIDC Core 1.0
- RFC 7235
- RFC 7617
- RFC 6749
- RFC 6750
- RFC 7519
- RFC 7636
- RFC 8414
- RFC 8705
- RFC 9110 framework-owned semantics
- WebSockets
- static files
- cookies
- streaming responses
- built-in middleware catalog

## Missing current-target surfaces

- RFC 9449 DPoP
- AsyncAPI docs UI
- JSON Schema docs UI
- OIDC discovery/docs surface
- WHATWG SSE
- forms / multipart
- upload handling
- unified `tigrbl` CLI and its command/flag surface

## Certification status

The current repository state does **not** justify a claim that the package is already certifiably fully featured or certifiably fully RFC/spec/standard compliant within the current boundary. This checkpoint documents the state honestly and freezes the authority surfaces needed to continue the program.
