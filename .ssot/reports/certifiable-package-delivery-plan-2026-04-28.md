# Certifiable Package Delivery Plan - 2026-04-28

## Current state

The live registry is structurally valid, but the package is not yet certifiably
fully featured, fully conformant, or fully compliant.

- Features: 556 total; 192 implemented, 283 partial, 81 absent.
- Planning horizons: 154 current, 2 explicit, 55 next, 181 backlog, 136 future,
  28 out of bounds.
- Proof coverage: 144 features have no linked claims, 40 features have no linked
  tests, 245 claims are not verified, and 288 evidence rows are not passing.
- Profiles: all six active profiles are present but emit validation warnings for
  current profile evaluation.
- Issues: seven tracked issues are open or active in the registry, including
  auth/security surface gaps and active-line certification closure.
- Risks: active release-blocking risks remain for nonimplemented feature claims
  and profileless certification scope.

## Gap inventory

The blocking gaps fall into these package surfaces:

- Public operator surface: generated OpenAPI/OpenRPC security declarations,
  generated REST/JSON-RPC auth behavior, package-coordinate traceability, and
  operator-facing certification reports are incomplete.
- Runtime and protocol surface: protocol runtime granularity, event/subevent
  taxonomy, transport event chains, loop/error branch execution, callback and
  webhook runtime delivery, WebTransport, SSE/WebSocket streaming, and Rust
  parity remain partial or absent.
- Extension and plugin surface: hook selector matching, runtime-owned hook
  legality, plugin extension boundaries, SPIFFE TLS behavior, ACME CA KMS/PKCS11
  adapters, and app-level placeholder cryptographic behavior remain incomplete.
- Operational surface: bounded runtime queue/backpressure, completion-fence
  semantics, release certification gates, package import/build traceability, and
  current profile evaluation closure remain incomplete.
- Development surface: legacy claim groups without feature links, broad feature
  rows without claim/test/evidence closure, and incomplete ADR/SPEC/test/evidence
  proof chains prevent strenuous certification.
- Production hardening surface: authentication drift, external error
  sanitization, security-scheme propagation, production crypto adapters, and
  fail-closed unsupported-engine behavior need closure.

## Incomplete files and modules

The current checkout still contains explicit placeholders, stubs, or unsupported
execution branches in:

- `pkgs/apps/tigrbl_acme_ca/tigrbl_acme_ca/workers/queue.py`
- `pkgs/apps/tigrbl_acme_ca/tigrbl_acme_ca/key_mgmt/providers.py`
- `pkgs/apps/tigrbl_acme_ca/tigrbl_acme_ca/libs/sw_cert_service.py`
- `pkgs/apps/tigrbl_spiffe/src/tigrbl_spiffe/identity/svid_validator.py`
- `pkgs/apps/tigrbl_spiffe/src/tigrbl_spiffe/tls/adapters.py`
- `pkgs/engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/session.py`
- `pkgs/engines/tigrbl_engine_dataframe/src/tigrbl_engine_dataframe/df_session.py`
- `pkgs/engines/tigrbl_engine_duckdb/src/tigrbl_engine_duckdb/duck_session.py`
- `pkgs/engines/tigrbl_engine_numpy/src/tigrbl_engine_numpy/session.py`
- `pkgs/engines/tigrbl_engine_pandas/src/tigrbl_engine_pandas/session.py`
- `pkgs/engines/tigrbl_engine_redis/src/tigrbl_engine_redis/session.py`
- `pkgs/engines/tigrbl_engine_xlsx/src/tigrbl_engine_xlsx/session.py`
- `pkgs/core/tigrbl_base/tigrbl_base/_base/_session_base.py`
- `pkgs/core/tigrbl_base/tigrbl_base/_base/_router_base.py`
- `pkgs/core/tigrbl_base/tigrbl_base/_base/_engine_base.py`
- `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_session.py`
- `pkgs/core/tigrbl_atoms/tigrbl_atoms/types.py`
- `pkgs/core/tigrbl_canon/tigrbl_canon/mapping/passes.py`

Some base-class `NotImplementedError` uses are legitimate abstract contracts.
They still need explicit SSOT classification so certification does not confuse
abstract surfaces with incomplete production behavior.

## Delivery plan

### Registry Truth Closure

Make the registry the hard gate for certification. Classify every nonimplemented
feature as current, next, backlog, future, explicit, or out of bounds; link every
current/explicit feature to a claim, test, and evidence row; remove or supersede
legacy claim groups that cannot identify covered features; and require profile
evaluation to pass without warnings.

### Public Contract Closure

Finish generated OpenAPI/OpenRPC security propagation, generated REST/JSON-RPC
auth behavior, default root behavior, external error sanitization, package
coordinate traceability, and operator documentation. Each public contract feature
must have an executable contract test and passing evidence.

### Runtime Conformance Closure

Close protocol runtime, transport dispatch, phase-tree, loop/error branch,
streaming, SSE, WebSocket, callback, webhook, and Rust parity gaps. Runtime
features must be proven across Python and Rust where a parity claim exists.

### Extension Surface Closure

Separate hook, plugin, SPIFFE, ACME CA, KMS, PKCS11, TLS, and adapter surfaces.
Each abstract extension point must be classified as an abstract contract, and
each production adapter must either be implemented and tested or explicitly out
of bounds.

### Engine and Storage Closure

Define per-engine support profiles for memory, SQLite/Postgres-backed OLTP, file
and dataframe engines, Redis, DuckDB, ClickHouse, Pandas, NumPy, and XLSX. For
engines that intentionally support a limited SQL statement subset, expose that as
documented capability metadata and fail closed on unsupported statements.

### Production Hardening Closure

Add fail-closed auth/security tests, queue/backpressure limits, runtime metrics,
crypto adapter validation, error-boundary tests, package import/build checks, and
release-blocking certification gates. Release certification should fail until
all current/explicit features meet their target assurance tier.

### Certification Closure

Run status convergence, full package test suites, build/import checks, SSOT
validation, profile evaluation, boundary certification, release certification,
promotion gate evaluation, and publication gate evaluation. Archive the closure
evidence under `.ssot/reports` and link the evidence to the active release.

## Required changes

- Convert 81 absent and 283 partial features into implemented, out of bounds, or
  explicitly scheduled backlog rows backed by current code evidence.
- Add claim/test/evidence links for 144 unclaimed features and test links for 40
  untested features.
- Verify or retire 245 currently unverified claims and refresh 288 non-passing
  evidence rows.
- Close seven tracked issues or mark them nonblocking with accepted risk.
- Mitigate or accept all active release-blocking risks.
- Make all active profiles evaluate without warnings.
- Require full release certification to include both code tests and SSOT proof
  chain validation.
