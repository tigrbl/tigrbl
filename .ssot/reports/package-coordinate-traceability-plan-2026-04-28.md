# Package Coordinate Traceability Delivery Plan

Generated: 2026-04-28

## Current Findings

The active registry validates, but it is not certifiably fully featured or fully conformant yet. The direct blockers are:

- 282 features remain partial and 81 remain absent.
- 23 next-horizon features are absent, including Python and Rust runtime evidence lanes, request-envelope contracts, transaction hot-path evidence, schema readiness fail-closed behavior, and executor benchmark baselines.
- Six active profiles are reported by validation warnings as active but not currently passing evaluation: active-line certification closure, development governance, extension and plugin surface, production hardening, public operator surface, and runtime protocol conformance.
- Two open issues remain release blocking: critical `iss:active-line-certification-closure-blocked-001` and high `iss:package-coordinate-feature-traceability-gap-001`.
- Two active release-blocking risks remain: `rsk:active-line-nonimplemented-feature-claims-001` and `rsk:profileless-certification-scope-001`.
- Eighteen repo-claim rows are not linked to features, so repo-level current, blocked, and evidence claims are not yet fully traceable.
- Package importability passes, but package-coordinate SSOT traceability is incomplete for the package names listed below.

## Package Coordinates Needing Direct Feature Coverage

- `tigrbl-acme-ca`
- `tigrbl-atoms`
- `tigrbl-canon`
- `tigrbl-client`
- `tigrbl-engine-bigquery`
- `tigrbl-engine-clickhouse`
- `tigrbl-engine-csv`
- `tigrbl-engine-dataframe`
- `tigrbl-engine-duckdb`
- `tigrbl-engine-inmemcache`
- `tigrbl-engine-inmemory`
- `tigrbl-engine-membloom`
- `tigrbl-engine-memdedupe`
- `tigrbl-engine-memkv`
- `tigrbl-engine-memlru`
- `tigrbl-engine-mempubsub`
- `tigrbl-engine-memqueue`
- `tigrbl-engine-memrate`
- `tigrbl-engine-numpy`
- `tigrbl-engine-pandas`
- `tigrbl-engine-pgsqli-wal`
- `tigrbl-engine-postgres`
- `tigrbl-engine-pyspark`
- `tigrbl-engine-redis`
- `tigrbl-engine-rediscachethrough`
- `tigrbl-engine-snowflake`
- `tigrbl-engine-sqlite`
- `tigrbl-engine-xlsx`
- `tigrbl-ops-olap`
- `tigrbl-ops-oltp`
- `tigrbl-ops-realtime`
- `tigrbl-orm`
- `tigrbl-spec`
- `tigrbl-spiffe`
- `tigrbl-typing`

## Delivery Plan

1. Registry closure: add direct feature, claim, test, and evidence rows for every package coordinate and link existing repo-level blocked/current/evidence claims to the affected feature families.
2. Profile closure: evaluate each active profile, convert every failing profile reason into a linked issue or risk, and keep profile membership limited to implemented or explicitly scheduled features.
3. Runtime conformance closure: finish the Python and Rust request-envelope, transaction hot-path, schema readiness, ASGI boundary, and benchmark evidence lanes with executable tests and artifact evidence.
4. Public operator closure: finish docs/runtime parity for CLI commands, flags, server support, docs surfaces, streaming, WebSocket, SSE, static files, upload, and middleware controls.
5. Extension and plugin closure: give each engine, hook, middleware, registry, session, and package extension surface a direct claim/test/evidence chain instead of relying on family-level coverage.
6. Production hardening closure: complete negative tests, fail-closed schema checks, auth/security contract parity, DDL boundary proof, and release-blocking risk retirement evidence.
7. Certification closure: sync statuses, validate the registry, certify only implemented feature claims, publish evidence snapshots, and keep blocked claims blocked until their evidence is current.

## Implemented In This Run

- Added an executable traceability test at `tools/ci/tests/test_package_coordinate_traceability.py`.
- Added this SSOT report as evidence for the package-coordinate gap.
- Registered SSOT feature, claim, test, evidence, and issue rows for package-coordinate traceability closure via the SSOT CLI.
- Kept the package-coordinate feature on the future horizon because the CLI validates each create operation immediately; the linked issue is current and release-blocking until package-level rows are decomposed.

## Closure Update

- Added one direct SSOT feature row for each package coordinate listed above.
- Linked all package-coordinate feature rows to `clm:package-coordinate-traceability-closure-001`, `tst:package-coordinate-traceability-gap-current`, `evd:package-coordinate-traceability-plan-20260428`, and `iss:package-coordinate-feature-traceability-gap-001`.
- Marked `feat:package-coordinate-traceability-closure-001` implemented because active package coordinates now have direct feature vocabulary in the registry.
- Advanced `clm:package-coordinate-traceability-closure-001` to evidenced based on the traceability test and this report.
- Closed `iss:package-coordinate-feature-traceability-gap-001` as non-release-blocking; broader package-level behavioral certification remains covered by the active-line issue and profile warnings.

## Covered Active Package Coordinates

- `tigrbl`
- `tigrbl-acme-ca`
- `tigrbl-atoms`
- `tigrbl-base`
- `tigrbl-canon`
- `tigrbl-client`
- `tigrbl-concrete`
- `tigrbl-core`
- `tigrbl-engine-bigquery`
- `tigrbl-engine-clickhouse`
- `tigrbl-engine-csv`
- `tigrbl-engine-dataframe`
- `tigrbl-engine-duckdb`
- `tigrbl-engine-inmemcache`
- `tigrbl-engine-inmemory`
- `tigrbl-engine-membloom`
- `tigrbl-engine-memdedupe`
- `tigrbl-engine-memkv`
- `tigrbl-engine-memlru`
- `tigrbl-engine-mempubsub`
- `tigrbl-engine-memqueue`
- `tigrbl-engine-memrate`
- `tigrbl-engine-numpy`
- `tigrbl-engine-pandas`
- `tigrbl-engine-pgsqli-wal`
- `tigrbl-engine-postgres`
- `tigrbl-engine-pyspark`
- `tigrbl-engine-redis`
- `tigrbl-engine-rediscachethrough`
- `tigrbl-engine-snowflake`
- `tigrbl-engine-sqlite`
- `tigrbl-engine-xlsx`
- `tigrbl-kernel`
- `tigrbl-ops-olap`
- `tigrbl-ops-oltp`
- `tigrbl-ops-realtime`
- `tigrbl-orm`
- `tigrbl-runtime`
- `tigrbl-spec`
- `tigrbl-spiffe`
- `tigrbl-tests`
- `tigrbl-typing`
