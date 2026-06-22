# Tigrbl Product Portfolio Website Brief

Audience: copywriting, technical writing, developer relations, design, and website implementation teams.

Purpose: provide a source-grounded brief for updating the Tigrbl product portfolio website. This is not a replacement for the SSOT registry, package READMEs, or release evidence. It is a website planning artifact derived from the current repository checkout.

Last researched from repo: 2026-06-22.

## Executive Summary

Tigrbl is a schema-first Python framework family for building ASGI APIs where one authoring model projects into REST, JSON-RPC, HTTP streaming, SSE, WebSocket, WebTransport-aware runtime planning, OpenAPI, OpenRPC, diagnostics, hooks, typed request/response models, and engine-backed handlers.

The website should present Tigrbl as a product portfolio, not as a single monolithic package. The app-facing product is the `tigrbl` facade package. Behind it is a governed package family: core specs, base contracts, concrete adapters, atoms, kernel planning, runtime execution, operation packs, ORM helpers, client tooling, testing utilities, and engine plugins.

The strongest public story is:

- Schema-first application authoring through `tigrbl`.
- REST, JSON-RPC, streaming, SSE, WebSocket, and WebTransport-aware runtime projection from the same operation inventory.
- OpenAPI 3.1, OpenRPC, Swagger UI, Lens/OpenRPC UI, and JSON Schema bundle output.
- Lifecycle hooks, kernel plans, diagnostics, typed schemas, and operation packs.
- Engine plugin portfolio for databases, in-memory services, cache, queue, rate limiting, dataframes, files, and warehouses.
- Operator and dev workflows through a unified `tigrbl` CLI.
- Governed release and proof discipline through SSOT records, package-local READMEs, conformance docs, and CI workflows.

The website must avoid overstating support:

- Tigrbl does not ship an application product from this repo.
- Tigrbl does not ship a built-in monitoring dashboard.
- Tigrbl can support app-defined live streams through SSE and WebSockets, but it does not currently ship a framework-owned live operational event console.
- WebTransport is present as a provisional/partial line and demo surface, not a mature release-grade transport story.
- HTTP/1.1, HTTP/2, HTTP/3, QUIC, HPACK, QPACK, TLS termination, ALPN, and flow control are server/runtime-layer concerns; Tigrbl documents binding, planning, framing, and capability boundaries rather than claiming full wire-protocol ownership.
- AsyncAPI generation, mounting, and UI are de-scoped in current docs and should not be advertised as supported.

## Primary Positioning

Recommended one-line positioning:

> Tigrbl is a schema-first Python framework for projecting one governed authoring model across REST, JSON-RPC, streaming, SSE, WebSocket, transport-aware runtime plans, OpenAPI/OpenRPC docs, typed contracts, lifecycle hooks, and pluggable engines.

Short version:

> Schema-first Python APIs with REST, JSON-RPC, streaming, WebSocket, typed contracts, runtime plans, and engine plugins.

Developer-oriented version:

> Define application behavior once with Tigrbl specs, operations, hooks, and engines; project it into REST, JSON-RPC, HTTP streams, SSE, WebSocket channels, OpenAPI, OpenRPC, diagnostics, schemas, and runtime execution.

Portfolio-oriented version:

> Tigrbl is a governed Python framework portfolio: an app-facing facade package, split framework layers, operation packs, clients, testing utilities, and engine plugins for data, cache, queues, warehouses, and runtime workflows.

## What Tigrbl Is

Tigrbl is:

- A schema-first Python ASGI framework family.
- A public facade package named `tigrbl`.
- A workspace of split packages for framework authors and extension authors.
- A REST, JSON-RPC, streaming, SSE, WebSocket, and transport-aware runtime projection system.
- A typed contract and documentation generation surface.
- A runtime planning and execution pipeline.
- An engine plugin ecosystem.
- A governed repository with SSOT-backed claims, evidence, release bundles, package docs, and CI gates.

Tigrbl is not:

- A single import-only package with no internal product structure.
- A business application or SaaS product.
- A FastAPI or Starlette application authoring pattern.
- A direct SQLAlchemy authoring pattern for application code.
- A built-in observability dashboard.
- A mature WebTransport platform claim in the current checkout.
- An AsyncAPI product line.

## Core Value Propositions

### 1. One Authoring Model, Multiple Surfaces

Tigrbl application behavior is authored once and projected across REST, JSON-RPC, OpenAPI, OpenRPC, diagnostics, schemas, hooks, runtime plans, and engine-backed handlers.

Website implication: show a central "operation model" or "spec-first service" that fans out to REST, JSON-RPC, OpenAPI, OpenRPC, schemas, diagnostics, hooks, and engines.

### 2. Stable Facade, Split Internals

Application teams normally install and import `tigrbl`. Framework maintainers, extension authors, and package owners can work at narrower package layers such as `tigrbl-core`, `tigrbl-base`, `tigrbl-concrete`, `tigrbl-runtime`, `tigrbl-atoms`, and `tigrbl-kernel`.

Website implication: make the home page simple, then give the portfolio page a layered package map.

### 3. Protocol and Documentation Parity

REST, JSON-RPC, HTTP streaming, SSE, and WebSocket are first-class surfaces. WebTransport is a provisional/partial active line. OpenAPI, OpenRPC, Swagger UI, Lens/OpenRPC UI, and JSON Schema bundle output are documented operator surfaces.

Website implication: include an "API and transport projection" section that shows REST, RPC, streaming, SSE, WebSocket, and carefully labeled WebTransport-aware planning as parts of the same operation model, not REST as the only product.

### 4. Lifecycle and Governance

Tigrbl uses specs, operations, hooks, kernel plans, runtime phases, and SSOT-backed release evidence. This gives teams a way to keep routes, schemas, docs, diagnostics, and runtime behavior aligned.

Website implication: use "governed" and "provable" carefully. It is valid to talk about SSOT-governed releases and evidence, but avoid vague compliance claims.

### 5. Engine Plugin Portfolio

Tigrbl publishes or tracks engines for SQL databases, in-memory utilities, Redis, files, dataframes, arrays, Spark, and warehouses.

Website implication: make engines a full portfolio section with categories, not a footnote.

## Target Audiences

### Application Developers

Need to know:

- Install `tigrbl`.
- Use `TigrblApp`, `TigrblRouter`, facade decorators, table helpers, column helpers, operation specs, hook specs, response decorators, schema helpers, and engine decorators.
- Avoid FastAPI/Starlette route authoring as the application pattern.
- Avoid raw SQLAlchemy columns as the primary application field authoring model when Tigrbl specs can express the behavior.

Primary website goal:

- Get them from "what is this?" to a small app shell, docs output, and operation projection quickly.

### Platform Teams

Need to know:

- Tigrbl aligns REST, JSON-RPC, schemas, docs, diagnostics, hooks, and runtime behavior.
- CLI surfaces support `run`, `serve`, `dev`, `routes`, `openapi`, `openrpc`, `doctor`, and `capabilities`.
- Serving paths include Uvicorn, Hypercorn, Gunicorn, and Tigrcorn when available.
- Operator knobs include docs paths, server choice, WebSocket heartbeat, metrics export configuration, H2/H3 tuning, TLS policy, deployment profiles, and other runner-facing controls.

Primary website goal:

- Show operational clarity without claiming a built-in monitoring product.

### Extension Authors

Need to know:

- Split packages have defined boundaries.
- Engines and operation packs are intentional plugin surfaces.
- Lower-level packages should be used when implementing framework boundaries, not ordinary app code.

Primary website goal:

- Give package map, engine extension model, and contribution pointers.

### Technical Buyers / Evaluators

Need to know:

- Tigrbl is governance-heavy, release-evidence-oriented, and package-boundary-aware.
- It is useful when teams need API behavior, docs, schemas, and runtime execution to stay aligned.
- It is not a low-ceremony microframework pitch.

Primary website goal:

- Make the risk-reduction story concrete: fewer duplicated definitions, clearer contract surfaces, explicit package boundaries, and evidence-backed release discipline.

## Recommended Website Information Architecture

### 1. Home

Goal: explain the product in one screen and route visitors to the right depth.

Recommended sections:

- Hero: "Schema-first Python APIs with REST, JSON-RPC, typed contracts, runtime plans, and engine plugins."
- Quick install: `uv add tigrbl` and `pip install tigrbl`.
- One authoring model fan-out: REST, JSON-RPC, OpenAPI, OpenRPC, schemas, diagnostics, hooks, engines.
- Why Tigrbl: consistency across API behavior, docs, schemas, diagnostics, and runtime plans.
- Portfolio preview: facade, specs, runtime, operation packs, engines.
- Honest support callout: current strong surfaces vs active/provisional lines.
- CTA: docs, GitHub, PyPI, package portfolio, examples.

### 2. Product Portfolio

Goal: show Tigrbl as a package family.

Recommended sections:

- Facade: `tigrbl`.
- Framework layers: core, base, concrete, atoms, kernel, runtime, ORM, typing.
- Operation packs: OLTP, OLAP, realtime.
- Developer utilities: client, tests, spec support.
- Engine portfolio: SQL, cache/KV, queue/pubsub/rate, dataframes/files, warehouses.
- Deprecated/compatibility boundaries: mention compatibility only where needed; do not foreground deprecated packages in product cards.

### 3. Build With Tigrbl

Goal: teach correct application authoring.

Recommended sections:

- App shell with `TigrblApp` and `TigrblRouter`.
- Route/decorator example.
- Table/operation/schema example.
- Hook lifecycle overview.
- Engine binding overview.
- REST, JSON-RPC, streaming, SSE, and WebSocket projection from one operation inventory.
- OpenAPI/OpenRPC/docs generation.

Do not use FastAPI or Starlette route examples as the primary teaching path.

### 4. Protocols and Docs

Goal: explain runtime and documentation projection.

Recommended sections:

- REST over HTTP/HTTPS.
- JSON-RPC over HTTP/HTTPS.
- HTTP streaming.
- SSE.
- WebSocket.
- WebTransport as provisional/partial.
- HTTP/2, HTTP/3, and QUIC as delegated serving/runtime concerns, not framework-owned wire-protocol claims.
- OpenAPI 3.1 and Swagger UI.
- OpenRPC and Lens/OpenRPC UI.
- JSON Schema bundle.
- Unsupported: AsyncAPI generation/mounting/UI.

### 5. Operations and Runtime

Goal: explain how Tigrbl moves from spec to execution.

Recommended sections:

- Specs, operations, hooks, kernel plan, runtime phases.
- Default CRUD semantics.
- Bulk, analytical, realtime, streaming, pub/sub, and transport-oriented operation packs.
- Diagnostics: `/system/healthz`, `/system/methodz`, `/system/hookz`, `/system/kernelz`.
- CLI: `run`, `serve`, `dev`, `routes`, `openapi`, `openrpc`, `doctor`, `capabilities`.

### 6. Engines

Goal: make backend support tangible.

Recommended groupings:

- SQL and transactional: SQLite, PostgreSQL, PostgreSQL/SQLite WAL.
- Analytical databases and warehouses: DuckDB, ClickHouse, BigQuery, Snowflake.
- Dataframes, arrays, and files: DataFrame, pandas, NumPy, PySpark, CSV, XLSX.
- In-memory infrastructure: in-memory database, KV, cache, LRU, Bloom, dedupe, queue, pub/sub, rate limiting.
- Redis: Redis and Redis cache-through.

### 7. Governance and Releases

Goal: explain evidence without overwhelming visitors.

Recommended sections:

- SSOT-governed workspace.
- Package-local READMEs and docs tree.
- CI workflows for release, branch coverage, gate validation, policy governance, evidence lanes, and CLI smoke.
- Conformance docs and release evidence.
- Apache 2.0 license.

Avoid vague "certified secure" or "standards compliant" language unless tied to specific release evidence.

### 8. Examples

Goal: provide practical entry points.

Recommended examples:

- Small app shell.
- REST and JSON-RPC operation parity.
- OpenAPI/OpenRPC generation.
- WebSocket and SSE app-defined live streams.
- Transport demo with careful labeling around WebTransport provisional status.
- Engine binding examples.

## Product Portfolio Detail

### Application-Facing Facade

| Package | Import root | Website role | Summary |
|---|---|---|---|
| `tigrbl` | `tigrbl` | Primary product | Schema-first ASGI framework facade for REST, JSON-RPC, OpenAPI, OpenRPC, SQLAlchemy-backed behavior, typed validation, hooks, engines, and CLI workflows. |

### Core Framework Layers

| Package | Import root | Website role | Summary |
|---|---|---|---|
| `tigrbl-core` | `tigrbl_core` | Spec authority | Core specs, decorators, schemas, hooks, operations, bindings, engines, storage, paths, docs, sessions, and middleware primitives. |
| `tigrbl-base` | `tigrbl_base` | Base contracts | Abstract contracts for apps, routers, tables, sessions, middleware, requests, responses, bindings, security, storage, and engine interfaces. |
| `tigrbl-concrete` | `tigrbl_concrete` | Lowering/adapters | Concrete implementations for reusable framework behavior, sessions, routes, responses, requests, security, decorators, engines, systems, and transports. |
| `tigrbl-atoms` | `tigrbl_atoms` | Runtime units | Phase names, stages, typed contexts, event anchors, protocol execution, and composable pipeline algebra. |
| `tigrbl-kernel` | `tigrbl_kernel` | Planning | Kernel orchestration for runtime plans, bindings, operation dispatch, packed plans, protocol chains, lifecycle rows, event keys, and optimized ASGI execution. |
| `tigrbl-runtime` | `tigrbl_runtime` | Execution | Runtime pipeline helpers, route execution, channel handling, frame/transport units, and operation dispatch. |
| `tigrbl-orm` | `tigrbl_orm` | Storage helpers | SQLAlchemy-facing tables, mixins, columns, model helpers, and persistence primitives. |
| `tigrbl-typing` | `tigrbl_typing` | Shared typing | Typing protocols, aliases, generics, and shared type helpers for packages and extensions. |

### Operation Packs

| Package | Import root | Website role | Summary |
|---|---|---|---|
| `tigrbl-ops-oltp` | `tigrbl_ops_oltp` | Transactional operations | CRUD, bulk, REST, JSON-RPC, and database-backed operation handlers. |
| `tigrbl-ops-olap` | `tigrbl_ops_olap` | Analytical operations | Query-oriented and analytical operation boundaries for OLAP workloads and engine integrations. |
| `tigrbl-ops-realtime` | `tigrbl_ops_realtime` | Realtime operations | Realtime, streaming, datagram, WebSocket, and event operation handlers for ASGI runtimes. |

### Developer and Integration Utilities

| Package | Import root | Website role | Summary |
|---|---|---|---|
| `tigrbl_client` | `tigrbl_client` | Client package | Typed Python client for REST and JSON-RPC APIs with sync/async calls, nested resource helpers, and optional Pydantic validation. |
| `tigrbl_spec` | `tigrbl_spec` | Spec artifacts | Shared interfaces, protocol definitions, compatibility targets, generated schemas, and specification artifacts. |
| `tigrbl_tests` | `tigrbl_tests` | Test utilities | Reusable pytest fixtures, conformance assertions, integration helpers, examples, and package test utilities. |

### Engine Portfolio

| Category | Engine packages | Website message |
|---|---|---|
| SQL and transactional persistence | `tigrbl_engine_sqlite`, `tigrbl_engine_postgres`, `tigrbl_engine_pgsqli_wal` | Local and server-backed transactional storage through engine plugins. |
| Analytical databases and warehouses | `tigrbl_engine_duckdb`, `tigrbl_engine_clickhouse`, `tigrbl_engine_bigquery`, `tigrbl_engine_snowflake` | Embedded and cloud analytical sessions for query and warehouse workloads. |
| Dataframes, arrays, and files | `tigrbl_engine_dataframe`, `tigrbl_engine_pandas`, `tigrbl_engine_numpy`, `tigrbl_engine_pyspark`, `tigrbl_engine_csv`, `tigrbl_engine_xlsx` | Tabular, array, workbook, CSV, and distributed DataFrame integrations. |
| In-memory infrastructure | `tigrbl_engine_inmemory`, `tigrbl_engine_inmemcache`, `tigrbl_engine_memkv`, `tigrbl_engine_memlru`, `tigrbl_engine_membloom`, `tigrbl_engine_memdedupe`, `tigrbl_engine_memqueue`, `tigrbl_engine_mempubsub`, `tigrbl_engine_memrate` | Process-local storage, cache, queue, pub/sub, dedupe, Bloom filters, LRU, and rate-limit behavior for lightweight services and tests. |
| Redis | `tigrbl_engine_redis`, `tigrbl_engine_rediscachethrough` | Redis-backed data structures, cache behavior, and cache-through acceleration. |

## Supported Surface Messaging

Use these terms confidently:

- Schema-first API framework.
- Public Python facade package.
- REST, JSON-RPC, streaming, SSE, WebSocket, and transport-aware runtime projection.
- OpenAPI 3.1 emission.
- OpenRPC emission.
- Swagger UI and Lens/OpenRPC UI.
- JSON Schema bundle.
- Operation specs and lifecycle hooks.
- Runtime plans and kernel diagnostics.
- Engine plugins.
- WebSocket route surface.
- WHATWG SSE response surface.
- Unified CLI.
- SSOT-governed workspace.

Use these terms with qualifiers:

- Monitoring: "bounded diagnostics" is accurate; "monitoring dashboard" is not.
- Live event stream: "app-defined live streams through SSE/WebSocket" is accurate; "built-in live operational console" is not.
- WebTransport: say "provisional", "partial", or "tracked active line"; do not present as mature.
- HTTP/2, HTTP/3, QUIC, HPACK, QPACK, TLS termination, ALPN, and flow control: mention as delegated server/runtime-profile concerns where relevant, not as blanket framework-owned guarantees.
- Certification: tie to specific SSOT records, conformance docs, or release workflows.

Do not claim:

- Built-in uptime dashboards.
- Built-in connection-count, throughput, latency, or per-transport health boards.
- AsyncAPI generation, `/asyncapi.json`, or AsyncAPI UI support as a current product surface.
- Full OIDC discovery/docs surface.
- Full exact closure for OAuth/OIDC/JWT/PKCE/DPoP standards unless supported by explicit current release evidence.
- That application packages are owned in this workspace.
- That application authors should build with FastAPI or Starlette directly.

## Suggested Copy Blocks

### Homepage Hero

Headline:

Schema-first Python APIs, projected across REST, JSON-RPC, streaming, WebSocket, docs, and runtime.

Supporting copy:

Tigrbl lets teams define service behavior once with specs, operations, hooks, schemas, and engines, then project that behavior into REST, JSON-RPC, HTTP streams, SSE, WebSocket channels, OpenAPI, OpenRPC, diagnostics, and runtime execution.

Primary CTA:

Install `tigrbl`

Secondary CTA:

Explore the package portfolio

### Portfolio Intro

Tigrbl is a framework portfolio with a stable facade for application developers and split packages for framework layers, operation packs, clients, tests, specs, and engines. Most teams start with `tigrbl`; extension authors can work directly at the core, runtime, operation, or engine layer when they need a narrower boundary.

### Engine Section Intro

Engines let Tigrbl applications bind storage, cache, queue, pub/sub, rate, dataframe, file, and warehouse behavior without turning application code into a pile of one-off backend adapters.

### Governance Section Intro

Tigrbl is managed as a governed Python workspace. Package boundaries, docs, release evidence, conformance material, and SSOT metadata are kept explicit so website claims can be traced back to repository-owned proof.

### Accuracy Note

Tigrbl includes bounded diagnostics and app-defined streaming surfaces. It does not currently ship a built-in monitoring dashboard, and WebTransport should be described as provisional rather than a finished product line.

## Technical Writing Assignments

Technical writers should produce:

- A concise "Start here" guide centered on `tigrbl`, not split packages.
- A package portfolio guide that mirrors the facade/layers/ops/engines taxonomy.
- A protocol projection guide showing one operation exposed through REST, JSON-RPC, OpenAPI, OpenRPC, diagnostics, and schemas.
- A lifecycle guide covering specs, operations, hooks, kernel plans, runtime phases, and diagnostics.
- An engine guide with category-level installation and binding examples.
- An operator guide for CLI commands and docs/diagnostics surfaces.
- A support-level page that separates supported, partial/provisional, unsupported, and de-scoped surfaces.

Writing rules:

- Use `tigrbl` facade imports in application examples.
- Keep framework-internal imports for advanced/extension sections only.
- Use "Tigrbl-owned authoring surfaces" in guidance, but explain it plainly.
- Explain why direct FastAPI, Starlette, SQLAlchemy column, and direct session patterns are not the application-facing Tigrbl path.
- Link current claims to source docs or SSOT evidence where possible.

## Copywriting Assignments

Copywriters should produce:

- Homepage hero and supporting copy.
- Persona-specific benefit statements for application developers, platform teams, extension authors, and evaluators.
- Portfolio card copy for each package category.
- Engine category copy.
- Short CTAs for install, docs, GitHub, PyPI, examples, package portfolio, and governance.
- A claims-safe "what Tigrbl does not claim yet" section for support-level clarity.

Tone:

- Technical, precise, and credible.
- Avoid hype that cannot be tied to repo evidence.
- Prefer "align", "project", "govern", "bind", "inspect", "execute", and "extend" over vague productivity claims.

## Developer Relations Assignments

Developer relations should produce:

- A quickstart video or article: install `tigrbl`, create an app shell, expose a health endpoint, inspect docs.
- A REST, JSON-RPC, and streaming projection walkthrough.
- A hooks and lifecycle walkthrough.
- A docs generation walkthrough: OpenAPI, Swagger UI, OpenRPC, Lens, JSON Schema bundle.
- A WebSocket and SSE example with clear "app-defined stream" language.
- An engine-binding demo for SQLite or Postgres, plus a lightweight in-memory engine demo.
- A transport demo explainer that labels WebTransport as provisional and h11/h2/h3/QUIC mechanics as delegated server/runtime concerns.
- A "from FastAPI habits to Tigrbl authoring" migration article, focused on Tigrbl-owned surfaces.

Devrel should not publish demos that teach direct FastAPI/Starlette route authoring as the main pattern.

## Visual and Design Direction

Available repo assets:

- `docs/assets/tigrbl-logo-lockup.png`
- `docs/assets/tigrbl-logo-mark.png`
- `docs/assets/tigrbl-logo-lockup-black.png`
- `docs/assets/tigrbl-developer-hero.png`
- `docs/assets/tigrbl-package-graph.png`
- `docs/assets/tigrbl-package-graph-core-engines-no-canon.png`
- `docs/assets/tigrbl-social-preview.png`
- README banner images for workspace, package line, docs, governance, and development.

Recommended visuals:

- Homepage hero: actual Tigrbl visual asset, not generic abstract gradients.
- Package portfolio: layered package map.
- Projection model: one authored operation feeding REST, JSON-RPC, OpenAPI, OpenRPC, schemas, diagnostics, hooks, runtime.
- Engine matrix: category grid by backend type.
- Governance: compact evidence flow from SSOT registry to docs, CI, release evidence, package READMEs.

Avoid visuals that imply:

- A built-in monitoring dashboard.
- Full WebTransport maturity.
- A SaaS application product owned by this repo.

## Website Content Gaps to Resolve

These should be resolved before final website publication:

1. Version consistency.
   - Live package metadata in this checkout reports package version `0.4.3` for the main package line.
   - The root README surface table still says "Current package line `0.4.1`".
   - Some conformance docs preserve older `0.3.x` release history.
   - Website should pick a single current version source and label historical release docs clearly.

2. Package catalog consistency.
   - `docs/developer/PACKAGE_CATALOG.md` lists 15 core packages and 22 engine packages, but live package metadata includes `tigrbl-ops-realtime` and 24 engine directories in `pkgs/engines`.
   - The catalog also references `tigrbl_canon` as a core package while the live tree places it under `pkgs/deprecated`.
   - Website should use a refreshed package inventory before publishing package counts.

3. Encoding cleanup.
   - Some docs render status icons as mojibake in this checkout.
   - Website copy should use plain words for support status until source encoding is cleaned.

4. WebTransport claims.
   - Transport demo docs include a WebTransport session demo but explicitly call the boundary provisional.
   - Website should not promote WebTransport as fully supported until release evidence says so.

5. Monitoring product language.
   - Diagnostics exist; a monitoring dashboard does not.
   - Website should avoid dashboard screenshots or feature cards unless a product surface is added later.

6. AsyncAPI references.
   - Some demo material lists `/asyncapi.json`, while support docs mark AsyncAPI generation and UI unsupported/de-scoped.
   - Website should avoid AsyncAPI claims unless the repo resolves that contradiction.

## Source Map

Primary source files used for this brief:

- `README.md`
- `pkgs/core/tigrbl/README.md`
- `pyproject.toml`
- `docs/README.md`
- `docs/developer/AUTHORING_BCP.md`
- `docs/developer/CLI_REFERENCE.md`
- `docs/developer/API_REFERENCE.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/OPERATOR_SURFACES.md`
- `docs/developer/TRANSPORTS_AND_FRAMING.md`
- `docs/developer/operator/websockets-and-sse.md`
- `docs/monitoring-and-transport-support-matrix.md`
- `docs/appspec-internal-spec-matrix.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/governance/README.md`
- `examples/transport_demo/README.md`
- Package metadata from `pkgs/core/*/pyproject.toml` and `pkgs/engines/*/pyproject.toml`.
