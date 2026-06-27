# Convenient Authoring Path and Best Current Practice (BCP)

This document defines the best current practice for application-facing Tigrbl
authoring. It is a developer guide over governed SSOT and package boundaries;
it does not replace `.ssot/` ADRs, specs, claim records, release evidence, or
certification reports.

Tigrbl is most convenient when application code describes behavior once and
lets the framework project that behavior into routes, RPC methods, schemas,
docs, lifecycle hooks, diagnostics, tests, and transport-aware runtime plans.
The best current practice is to use tables, default canonical operations,
operation specs, custom handlers, and lifecycle hooks together instead of
spreading one behavior across lower-level framework surfaces.

## How To Read This BCP

Each best-practice group explains what to avoid or not do, what to do instead,
and why the Tigrbl path is more convenient.

- `Avoid` means legal but not ideal for application-facing code. These paths
  are usually lower-level conveniences that can create drift, duplicated rules,
  or behavior that Tigrbl diagnostics and lifecycle phases cannot see.
- `Do not` means unsupported as normal application authoring. It is not a
  global repository ban; use the allowed-exception rules below when
  implementing or validating a lower-level framework boundary.
- `Do` means supported and preferred for application-facing code. These paths
  are expected to project cleanly into REST, JSON-RPC, HTTP streams, SSE,
  WebSocket, WebTransport-aware runtime planning, docs, diagnostics, hooks,
  schemas, tests, and engine behavior.
- `Why` explains the convenience, alignment, or safety reason for the rule.
- Runtime legality terms such as `required`, `optional`, `forbidden`,
  `illegal`, and `unsupported` belong to kernel/runtime protocol matrices.
  They decide whether a compiled binding, phase, atom, or framing plan is
  accepted or fails closed; they are related to this BCP but are not a
  replacement for authoring guidance.

## Scope

This BCP applies to application code, examples, product packages, service
skeletons, and README snippets that teach users how to build with Tigrbl.

This BCP does not ban implementation dependencies inside framework internals,
engine adapters, compatibility layers, benchmarks, or tests when those surfaces
are explicitly validating or implementing the lower-level boundary.

## Best Current Practice Groups

### Keep the facade as the application contract

- Avoid: Treating ASGI, FastAPI, Flask, Starlette, SQLAlchemy ORM
  materialization, or direct database/session calls as the user-facing
  application contract.
- Do: Build application services with `TigrblApp`, `TigrblRouter`, facade
  decorators, table helpers, column helpers, operation specs, hook specs,
  binding specs, engine specs, and generated schemas.
- Why: Tigrbl-owned authoring surfaces are the entry points that runtime
  planning, docs, diagnostics, schemas, and tests understand.

### Start with tables and default canonical operations

- Avoid: Hand-writing endpoint-specific behavior before checking whether
  table-backed default operations already express it.
- Do: Model resources with Tigrbl tables and use default canonical operations
  such as `create`, `read`, `update`, `replace`, `delete`, `list`, and `clear`
  where they fit.
- Why: Tables plus canonical operations give Tigrbl a durable resource model
  that can be projected consistently across REST, JSON-RPC, schemas, docs,
  hooks, diagnostics, and tests.

### Use operations and custom handlers for domain actions

- Avoid: Splitting one domain action across separate REST handlers, JSON-RPC
  handlers, stream handlers, docs snippets, and protocol-specific wrappers.
- Do: Model domain actions as Tigrbl operations with operation specs and custom
  handlers when the default canonical operations are not enough.
- Why: Operations are the unit Tigrbl can bind, document, inspect, test, and
  project across protocol surfaces.

### Use lifecycle hooks around operations

- Avoid: Embedding lifecycle policy directly inside transport-specific
  handlers or lower-level framework middleware.
- Do: Use lifecycle hooks around operations for validation, authorization,
  enrichment, auditing, response shaping, rollback handling, and post-response
  work.
- Why: Hooks make behavior visible before and after the operation, while
  preserving lifecycle ordering across REST, JSON-RPC, streams, SSE, WebSocket,
  and WebTransport-aware runtime plans.

### Support persistence and non-persistence operations

- Avoid: Assuming every operation or custom handler must be database-backed.
- Do: Use operations and custom handlers for persistence workflows and for
  non-persistence workflows such as computed responses, orchestration,
  control-plane commands, stream/session commands, or external-service actions.
- Why: The operation model gives both persistence and non-persistence behavior
  the same docs, hooks, diagnostics, protocol projection, and runtime planning
  path.

### Put field behavior in Tigrbl specs

- Avoid: Duplicating field behavior across SQLAlchemy declarations, Pydantic
  models, route handlers, and docs.
- Do: Describe field behavior through Tigrbl tables, `FieldSpec`,
  `ColumnSpec`, `StorageSpec`, and `IOSpec`.
- Why: These specs keep field semantics aligned for storage lowering,
  validation, schemas, docs, hooks, diagnostics, and runtime planning.

### Use generated schemas for operation payloads

- Avoid: Hand-written Pydantic envelopes for payloads that belong to a Tigrbl
  operation.
- Do: Use `get_schema(...)` or other Tigrbl schema helpers for operation
  request and response payloads.
- Why: Generated schemas keep payloads aligned with operation specs, docs,
  validation, and protocol projections.

### Keep engines and transactions declarative

- Avoid: Creating ad-hoc SQLAlchemy engines, sessions, sessionmakers, commits,
  or flushes inside application handlers.
- Do: Bind engines declaratively at app, router, table, or operation scope, and
  let kernel/runtime phases own dispatch and transaction progression.
- Why: Declarative binding lets the runtime own session selection, transaction
  scope, rollback behavior, pooling, diagnostics, backend adapters, and
  post-response work.

### Keep examples in Tigrbl style

- Avoid: README examples that present lower-level framework internals as normal
  application style.
- Do: Use Tigrbl facade imports and Tigrbl-owned authoring surfaces in
  application examples unless the example is explicitly marked as a lower-layer
  test, benchmark, migration, engine adapter, or framework-internal
  compatibility example.
- Why: Examples should show the framework path that keeps operations, schemas,
  docs, hooks, diagnostics, and runtime planning aligned.

### Keep workspace docs in their right lanes

- Avoid: Using the root README as the only documentation for a distributable
  package.
- Do: Use package-local README files to explain package boundaries, install
  targets, import roots, dependency surfaces, usage examples, and links to
  governed docs.
- Why: The root README orients the workspace, while package READMEs serve PyPI
  users who arrive at one install target.

### Do not wire endpoints around the operation plan

- Do not: Bypass operation specs, handlers, kernel plans, runtime atoms, or
  lifecycle phases with one-off route wrappers for REST, JSON-RPC, HTTP stream,
  SSE, WebSocket, or WebTransport behavior.
- Do: Define the operation once, bind it through Tigrbl specs, and let
  kernel/runtime planning own protocol dispatch.
- Why: This preserves legality checks, lifecycle phases, transaction ownership,
  protocol framing policy, and fail-closed unsupported-combination handling.

### Do not make lower-level frameworks the application surface

- Do not: Author Tigrbl application endpoints with FastAPI `FastAPI`,
  `APIRouter`, dependency wiring, route decorators, middleware registration,
  docs generation, or application lifecycle wiring.
- Do: Use Tigrbl app/router factories, decorators, tables, default canonical
  operations, operation specs, custom handlers, lifecycle hooks, schema helpers,
  and engine decorators.
- Why: FastAPI is a substrate here; Tigrbl is the application contract that
  keeps operations, bindings, hooks, schemas, docs, diagnostics, and tests
  together.

### Do not route around the runtime substrate boundary

- Do not: Author application endpoints directly with Starlette route, request,
  response, middleware, background-task, or application lifecycle classes.
- Do: Express application behavior through Tigrbl operations, bindings,
  lifecycle hooks, and runtime-managed execution.
- Why: Starlette is a lower-level runtime substrate here, not the
  application-facing authoring surface.

### Do not fragment behavior into Flask route objects

- Do not: Author application endpoints with Flask `Flask`, `Blueprint`, route
  decorators, request/response globals, `MethodView`, extension registration,
  or application lifecycle hooks.
- Do: Keep resources in tables, use default canonical operations where they
  fit, and use operation specs plus custom handlers for domain actions.
- Why: Flask route objects cannot preserve Tigrbl's shared operation inventory,
  schema generation, lifecycle phases, hook ordering, or transport plan.

### Do not use raw ORM declarations as the primary application model

- Do not: Use raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the
  primary application authoring surface when Tigrbl specs can represent the
  field behavior.
- Do: Describe field behavior through Tigrbl tables, `FieldSpec`,
  `ColumnSpec`, `StorageSpec`, and `IOSpec`.
- Why: Raw ORM declarations are only one lowering target and cannot carry the
  full storage, IO, validation, docs, hook, and runtime contract.

### Do not manage database state inside handlers

- Do not: Call direct database/session methods such as `flush()` or `commit()`
  from application hooks or handlers.
- Do: Let lifecycle phases such as `START_TX`, `PRE_HANDLER`, `HANDLER`,
  `POST_HANDLER`, `PRE_COMMIT`, and `TX_COMMIT` own transaction progression.
- Why: Direct calls bypass lifecycle guards and can commit partial state before
  hooks, errors, rollback handlers, or response shaping have run.

### Do not blur package boundaries

- Do not: Widen a package boundary by adding dependencies, imports, examples,
  or docs that belong in another split package.
- Do: Keep facade guidance in `tigrbl`, framework internals in the lower-level
  packages that own them, and package-specific usage in package-local READMEs.
- Why: Clear package boundaries make the split distribution convenient instead
  of surprising, especially for users installing only one package.

### Keep release and certification claims governed

- Avoid: Duplicating release, certification, target-state, or conformance
  claims outside governed evidence records.
- Do: Use `.ssot/`, conformance docs, release evidence, and certification
  reports for governed feature, claim, release, evidence, and target-state
  questions.
- Why: Release status and proof chains need one source of truth so package docs
  do not drift from CI and certification evidence.

## Allowed Exceptions

The following uses are allowed when the code or README names the boundary
clearly, such as benchmark, test fixture, migration compatibility, engine
adapter, concrete adapter, or framework-internal lowering.

### Use lower-level frameworks only for explicit boundary work

- Avoid: Presenting FastAPI, Starlette, Flask, or ASGI internals as the normal
  application authoring path.
- Do: Use those lower-level surfaces only when implementing, benchmarking,
  migrating, or testing a named compatibility or runtime boundary.
- Why: Boundary work sometimes needs the substrate directly, but application
  guidance should still point users to the Tigrbl contract.

### Use SQLAlchemy directly only in storage-owned boundaries

- Avoid: Treating SQLAlchemy storage constructs as the primary application
  model in public guidance.
- Do: Use SQLAlchemy directly in engine packages, storage lowering, reflection,
  datatype lowering, migrations, and compatibility tests.
- Why: SQLAlchemy is a legitimate implementation substrate when Tigrbl specs
  remain the source and SQLAlchemy is the generated or adapter-owned target.

### Preserve historical examples as history

- Avoid: Updating archived or deprecated docs to pretend they are current
  authoring guidance.
- Do: Leave historical examples in place when they are clearly archived,
  deprecated, or compatibility-only.
- Why: History can remain traceable without redefining the active recommended
  style.

## README And Example Requirements

### Keep public examples on the facade path

- Avoid: README snippets that teach lower-level framework internals as the
  ordinary way to build a Tigrbl application.
- Do: Use Tigrbl facade imports and Tigrbl-owned authoring surfaces in public
  application examples.
- Why: Public examples should lead readers to the framework path that keeps
  operations, schemas, docs, hooks, diagnostics, and runtime planning aligned.

### Mark exceptions plainly

- Avoid: Mixing lower-level benchmark, test fixture, migration, engine adapter,
  or compatibility examples into application guidance without a boundary note.
- Do: Say when an example is lower-layer, benchmark, test fixture, migration,
  engine adapter, concrete adapter, or framework-internal compatibility code.
- Why: Readers need to know whether the example is best practice,
  legal-but-lower-level, or compatibility-only.

### Keep detailed policy at governed entry points

- Avoid: Letting README summaries become a competing source of truth for
  authoring policy.
- Do: Keep detailed BCP guidance in this file, with the repository README and
  facade package README acting as concise entry-point summaries.
- Why: One canonical policy keeps package docs, examples, validators, and CI
  evidence aligned.
