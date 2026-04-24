# Current State — Phase 8 CLI Closure

## Scope and method

This document carries forward the Phase 7 docs/operator checkpoint and records the Phase 8 work completed against the unified framework CLI row.

Phase 8 focused on:

- implementing the unified `tigrbl` CLI surface inside the `tigrbl` package
- wiring the console entry point into the package metadata
- documenting the command surface and required flags in `docs/developer/CLI_REFERENCE.md`
- adding smoke coverage for every required command
- adding supported-server compatibility smoke for Uvicorn, Hypercorn, Gunicorn, and Tigrcorn runner dispatch
- updating the governed docs tree so the current state no longer implies that the CLI row is open

The current state below is grounded in:

1. direct code inspection of the Phase 8 tree
2. direct inspection of the governed documentation tree
3. execution of the repository policy validators under `tools/ci/`
4. execution of the Phase 8 CLI pytest slice preserved under `docs/conformance/audit/2026/p8-cli/`
5. carried-forward evidence from Phases 5 through 7 for the already-closed docs, spec, RFC, and operator rows

## Certification status

This checkpoint does **not** justify a Tier 3 current-boundary certification claim.

The repository is **not** honestly describable at this checkpoint as:

- certifiably fully featured
- certifiably fully RFC/spec/standard compliant

within the declared current target boundary.

The Phase 8 deliverable closes the last remaining current-target surface gap at Tier 2 checkpoint quality. The later evidence-lane, reproducibility, and promotion gates remain open.

## Exact CLI state

### Closed now

| Surface | Current state | Evidence |
|---|---|---|
| top-level `tigrbl` entry point | closed | `pkgs/core/tigrbl/pyproject.toml`, `pkgs/core/tigrbl/tigrbl/__main__.py`, `pkgs/core/tigrbl/tigrbl/cli.py` |
| `tigrbl run` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py` |
| `tigrbl serve` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py` |
| `tigrbl dev` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py` |
| `tigrbl routes` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py` |
| `tigrbl openapi` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py` |
| `tigrbl openrpc` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py` |
| `tigrbl doctor` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py` |
| `tigrbl capabilities` | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py` |
| required CLI flags | closed | `pkgs/core/tigrbl/tigrbl/cli.py`, `docs/developer/CLI_REFERENCE.md`, `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py` |
| supported-server compatibility smoke | closed at runner-dispatch smoke level | `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py` |

### Exact meaning of the current server smoke

The Phase 8 server smoke covers:

- command parsing
- command-to-runner dispatch
- configuration translation into the Uvicorn, Hypercorn, Gunicorn, and Tigrcorn runner layers
- docs-path / OpenAPI-path / OpenRPC-path / Lens-path mounting before serving

The Phase 8 smoke does **not** attempt a full installed-package, live-network, multi-process compatibility certification lane. That remains part of the later evidence/reproducibility gates.

## Exact docs/UI state

The current cycle still keeps and verifies:

- `/openapi.json`
- Swagger UI at `/docs`
- `/openrpc.json`
- Lens / OpenRPC UI at `/lens`
- `/schemas.json`
- `/asyncapi.json`

The current cycle still de-scopes:

- AsyncAPI UI
- JSON Schema UI
- OIDC discovery/docs surface

## Exact operator-surface state

The Phase 7 operator closure remains in force. The current cycle keeps closed status for:

- static files
- cookies
- streaming responses
- WebSockets
- WHATWG SSE
- forms / multipart
- upload handling
- bounded built-in middleware catalog
- generic auth kept dependency/hook-based only

## Exact current-target state summary

There are now **no unresolved current-target surface gaps** in the governed docs tree.

The current-target program is now in this position:

- docs/spec rows: closed or explicitly de-scoped
- retained RFC/security rows: closed or explicitly de-scoped
- docs/operator rows: closed or explicitly de-scoped
- CLI row: closed

## Evidence-backed conclusions

1. The repository now exposes a unified `tigrbl` CLI with the required command set and required flag set.
2. The current-target surface boundary has no remaining open implementation rows.
3. Gate B can now be treated as passed for the current cycle.
4. The remaining work is no longer surface closure; it is evidence-lane build-out, reproducibility, and release promotion.

## Authoritative companion documents

- `docs/conformance/IMPLEMENTATION_MAP.md`
- `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/audit/2026/p8-cli/README.md`
- `docs/developer/CLI_REFERENCE.md`
