# Authoring BCP

This document defines the best current practice for application-facing Tigrbl
authoring. It is a developer guide over the governed SSOT and package
boundaries; it does not replace `.ssot/` ADRs, specs, claim records, or release
evidence.

The short rule is: application code should describe service behavior through
Tigrbl-owned authoring surfaces, and lower-level packages should hide ASGI,
SQLAlchemy, runtime, and engine mechanics behind Tigrbl contracts.

## How To Read This BCP

- `Do` means supported and preferred for application-facing code. These paths are
  expected to project cleanly into REST, JSON-RPC, HTTP streams, SSE, WebSocket,
  WebTransport-aware runtime planning, docs, diagnostics, hooks, schemas, tests,
  and engine behavior.
- `Avoid` means legal but not ideal for application-facing code. These paths are
  usually lower-level conveniences that can create drift, duplicated rules, or
  behavior that Tigrbl diagnostics and lifecycle phases cannot see.
- `Do not` means unsupported as normal application authoring. It is not a global
  repository ban; use the allowed-exception rules below when implementing or
  validating a lower-level framework boundary.
- `Allowed Exceptions` means legal only when the code or README names the
  boundary clearly, such as benchmark, test fixture, migration compatibility,
  engine adapter, concrete adapter, or framework-internal lowering.
- Runtime legality terms such as `required`, `optional`, `forbidden`, `illegal`,
  and `unsupported` belong to kernel/runtime protocol matrices. They decide
  whether a compiled binding, phase, atom, or framing plan is accepted or fails
  closed; they are related to this BCP but are not a replacement for authoring
  guidance.

## Scope

This BCP applies to application code, examples, product packages, service
skeletons, and README snippets that teach users how to build with Tigrbl.

This BCP does not ban implementation dependencies inside framework internals,
engine adapters, compatibility layers, benchmarks, or tests when those surfaces
are explicitly validating or implementing the lower-level boundary.

## Tigrbl-Owned ASGI Boundary

Do:

- Do build application surfaces with `TigrblApp`, `TigrblRouter`, Tigrbl
  facade decorators, operation specs, binding specs, hook specs, and generated
  documentation surfaces. Why: these are the supported authoring entry points
  that the facade, runtime, docs, diagnostics, and tests understand.
- Do model a domain behavior once and let Tigrbl project it into REST,
  JSON-RPC, HTTP streams, SSE, WebSocket, WebTransport-aware runtime units,
  OpenAPI, OpenRPC, diagnostics, schemas, and runtime plans. Why: one operation
  inventory prevents each protocol surface from drifting into a different API.
- Do keep transport-specific behavior behind Tigrbl bindings, runtime atoms,
  concrete adapters, or engine/plugin boundaries. Why: stream, SSE, WebSocket,
  and WebTransport behavior needs kernel/runtime planning, lifecycle ownership,
  and fail-closed validation instead of ad-hoc route code.
- Do use Tigrbl diagnostics such as `/system/methodz`, `/system/hookz`, and
  `/system/kernelz` when checking what the framework actually registered. Why:
  diagnostics expose the compiled Tigrbl state rather than a lower-level
  framework's partial view of the app.

Do not:

- Do not author application endpoints with FastAPI `FastAPI`, `APIRouter`,
  dependency wiring, route decorators, middleware registration, or lifecycle
  hooks. Why: that makes FastAPI the application contract instead of Tigrbl's
  operation, binding, hook, schema, docs, and diagnostics contract.
- Do not author application endpoints with Starlette route, request, response,
  middleware, background-task, or lifecycle classes. Why: Starlette is a
  lower-level runtime substrate here, not the application-facing authoring
  surface.
- Do not author application endpoints with Flask `Flask`, `Blueprint`, route
  decorators, request/response globals, `MethodView`, extension registration,
  or lifecycle hooks. Why: Flask route objects cannot preserve Tigrbl's shared
  operation inventory, schema generation, lifecycle phases, or transport plan.
- Do not wrap Tigrbl model behavior in transport-specific route handlers when
  an operation spec can represent the behavior. Why: route wrappers hide
  behavior from REST/JSON-RPC projection, stream planning, docs, hooks,
  diagnostics, and tests.
- Do not use FastAPI or Starlette documentation generation as the source of
  truth for a Tigrbl surface. Why: Tigrbl docs must come from the same specs and
  operation inventory that runtime dispatch uses.
- Do not bypass kernel/runtime plans when wiring REST, JSON-RPC, HTTP stream,
  SSE, WebSocket, or WebTransport behavior. Why: bypasses skip legality checks,
  lifecycle phases, transaction ownership, protocol framing policy, and
  fail-closed unsupported-combination handling.

Avoid:

- Avoid treating ASGI as the author-facing API. ASGI is the runtime protocol
  boundary; Tigrbl is the authoring boundary. Why: ASGI exposes transport
  mechanics that should stay behind Tigrbl-owned adapters and runtime plans.
- Avoid adding one-off route wrappers that drift from the operation inventory.
  Why: the service may appear to work on one protocol while docs, diagnostics,
  schemas, hooks, or other protocol projections describe something else.
- Avoid transport-only shortcuts that make REST, JSON-RPC, streams, SSE,
  WebSocket, WebTransport, docs, diagnostics, and hooks disagree about what the
  service supports. Why: Tigrbl's value is one declared behavior projected
  across protocol surfaces with explicit support boundaries.

## Spec-First Table And Column Authoring

Do:

- Do express field behavior through Tigrbl table, column, datatype, storage,
  IO, request, response, and operation specs. Why: those specs are the shared
  source for storage lowering, wire schemas, docs, runtime planning, hooks, and
  diagnostics.
- Do use Tigrbl column helpers and `ColumnSpec`-backed metadata when a field
  belongs to a Tigrbl model. Why: helpers keep application models on Tigrbl's
  supported public surface while still allowing internals to lower into
  SQLAlchemy.
- Do keep storage intent, wire-schema intent, validation intent, defaulting,
  masking, ownership, tenancy, and operation visibility in specs that the
  schema/runtime/docs layers can read. Why: each layer needs the same field
  semantics to avoid hidden storage-only or schema-only behavior.
- Do let Tigrbl lower column intent into SQLAlchemy, Pydantic, engine-specific
  datatypes, runtime schemas, and documentation projections. Why: direct
  per-layer declarations duplicate logic and are easy to keep inconsistent.

Do not:

- Do not use raw SQLAlchemy `mapped_column(...)` as the primary application
  authoring surface when Tigrbl specs can express the column behavior. Why:
  raw ORM declarations are only one lowering target and cannot carry the full
  Tigrbl storage, IO, validation, docs, hook, and runtime contract.
- Do not use raw SQLAlchemy `Column(...)` as the primary application authoring
  surface when Tigrbl column helpers or specs can express the column behavior.
  Why: direct SQLAlchemy columns make storage shape look authoritative even
  when operation, schema, docs, and runtime behavior need richer metadata.
- Do not attach live sessions, request objects, transport handles, or engine
  instances to core specs. Why: specs must remain portable declarations that can
  be compiled, inspected, tested, and reused without live runtime state.
- Do not mutate compiled specs in place after runtime plans have been built.
  Why: compiled plans, schemas, docs, hooks, and diagnostics would no longer
  describe the same behavior.

Avoid:

- Avoid duplicating the same field rules in SQLAlchemy, Pydantic, docs, and
  request handlers. Put the reusable rule in the Tigrbl spec layer. Why:
  duplicated rules create stale validation, stale docs, and protocol-specific
  behavior differences.
- Avoid treating ORM materialization as the source of truth. SQLAlchemy is a
  lowering target for storage and inspection; Tigrbl specs are the authoring
  contract. Why: ORM materialization cannot by itself describe wire behavior,
  operation visibility, docs, hooks, diagnostics, or transport planning.
- Avoid hand-written Pydantic envelopes for payloads that belong to a Tigrbl
  operation; use `get_schema(...)` and schema helpers. Why: generated schemas
  keep request/response payloads aligned with operation specs and docs.
- Avoid using raw SQLAlchemy columns or direct ORM declarations as a temporary
  shortcut in public examples. Why: readers copy examples as the recommended
  style, and direct columns bypass the Tigrbl metadata needed by other layers.

## Operation, Handler, And Lifecycle Dispatch

Do:

- Do model domain verbs as canonical operations, operation-pack verbs, or
  explicit custom `OpSpec` entries. Why: operations are the unit that Tigrbl can
  project consistently into REST, JSON-RPC, streams, SSE, WebSocket,
  WebTransport-aware plans, docs, diagnostics, hooks, and tests.
- Do put policy, validation, enrichment, audit, and response shaping in hooks
  attached to the relevant phase. Why: hooks make policy visible to lifecycle
  ordering, diagnostics, tests, and transport-independent execution.
- Do use Tigrbl handlers through operation specs and kernel/runtime dispatch so
  REST, JSON-RPC, streams, SSE, WebSocket, WebTransport-aware runtime units,
  schemas, docs, hooks, and diagnostics stay aligned. Why: handler dispatch is
  where protocol projection and lifecycle guarantees meet.
- Do bind engines declaratively at app, router, table, or operation scope.
  Why: declarative binding lets the runtime own session selection, transaction
  scope, diagnostics, and backend-specific behavior.
- Do let runtime phases own transaction progression: `START_TX`,
  `PRE_HANDLER`, `HANDLER`, `POST_HANDLER`, `PRE_COMMIT`, `TX_COMMIT`,
  `POST_COMMIT`, and rollback/error phases. Why: transaction ownership must be
  ordered with handler execution, hooks, errors, rollback, and post-response
  work.

Do not:

- Do not call database direct methods such as `flush()` or `commit()` from
  application hooks or handlers. Why: direct calls bypass lifecycle guards and
  can commit partial state before hooks, errors, rollback handlers, or response
  shaping have run.
- Do not construct ad-hoc SQLAlchemy engines, sessions, or sessionmakers inside
  request handlers. Why: ad-hoc construction bypasses declarative engine
  binding, session policy, pooling, diagnostics, tests, and backend adapters.
- Do not bypass kernel/runtime plans when wiring REST, JSON-RPC, HTTP stream,
  SSE, WebSocket, or WebTransport handlers. Why: direct wiring skips binding
  legality, protocol framing, transaction units, lifecycle phases, and
  fail-closed unsupported-combination checks.
- Do not implement core persistence, transport emission, or transaction
  lifecycle by hand in user hooks. Why: those responsibilities belong to atoms,
  engine adapters, and lifecycle phases so every protocol path behaves
  consistently.
- Do not make route handlers the canonical business-logic surface when a Tigrbl
  handler or operation spec can represent the behavior. Why: route-owned
  business logic is invisible to operation inventory, generated schemas, docs,
  hooks, diagnostics, and non-REST protocol projections.

Avoid:

- Avoid direct DB/session mutation from application code. Put persistence
  semantics behind operations, handlers, atoms, engine adapters, and lifecycle
  phases. Why: lifecycle-owned persistence keeps transactions, rollback,
  diagnostics, and test evidence coherent.
- Avoid hiding behavior in route wrappers or ad-hoc dependencies that
  diagnostics cannot see. Why: invisible behavior cannot be checked through
  `/system/methodz`, `/system/hookz`, `/system/kernelz`, OpenAPI, OpenRPC, or
  proof tests.
- Avoid adding operation-specific policy at the transport layer when the same
  rule belongs in specs, hooks, or lifecycle phases. Why: transport-layer policy
  can make REST, JSON-RPC, streams, SSE, WebSocket, and WebTransport disagree
  about the same domain operation.
- Avoid direct SQLAlchemy session calls such as `add`, `delete`, `execute`,
  `flush`, `commit`, or `rollback` in app code when a Tigrbl operation or
  lifecycle phase can own the work. Why: direct mutation makes transaction
  timing and error behavior depend on local handler code instead of the runtime
  contract.

## Allowed Exceptions

The following uses are allowed when they are explicit about their boundary:

- Framework internals may use ASGI-compatible or Starlette-compatible behavior
  behind Tigrbl-owned concrete adapters. Why: internals sometimes need the
  lower-level serving substrate while still presenting a Tigrbl-owned authoring
  surface.
- Engine packages may use SQLAlchemy to implement engine, session, transaction,
  storage, reflection, and datatype-lowering behavior. Why: SQLAlchemy is a
  legitimate implementation substrate for engine and storage packages.
- Base/concrete internals may lower `ColumnSpec` and related metadata into
  SQLAlchemy constructs. Why: lowering is legal when Tigrbl specs remain the
  source and SQLAlchemy is the generated target.
- Tests, examples, and benchmarks may use FastAPI, Starlette, Flask,
  SQLAlchemy `Column(...)`, or SQLAlchemy `mapped_column(...)` when they are
  validating compatibility, parity, legacy behavior, migration behavior, or
  lower-level framework boundaries. Why: these uses are legal when they prove or
  compare a boundary instead of teaching normal application authoring.
- Deprecated and archived docs may preserve historical examples, but they are
  not current authoring guidance. Why: history can remain available without
  redefining the active recommended style.

When an exception is used, the code or README should make the boundary clear:
benchmark, test fixture, migration compatibility, engine adapter, concrete
adapter, or framework-internal lowering.

## README And Example Requirements

Do:

- Do make public README examples use Tigrbl facade imports and Tigrbl-owned
  authoring surfaces. Why: public examples are copied as the recommended app
  style.
- Do describe exceptions plainly when an example intentionally shows a lower
  layer, benchmark, test fixture, or compatibility path. Why: readers need to
  know whether the example is best practice, legal-but-lower-level, or a
  compatibility-only case.
- Do keep detailed BCP guidance in this file, the repository README, and the
  facade package README. Why: the policy needs to be visible at the entry points
  application developers actually read.

Do not:

- Do not teach FastAPI or Starlette route authoring as an application pattern in
  active Tigrbl README examples. Why: that moves the authoring contract away
  from Tigrbl-owned surfaces.
- Do not teach Flask route, blueprint, or `MethodView` authoring as an
  application pattern in active Tigrbl README examples. Why: those examples
  would teach a different framework model than Tigrbl's operation model.
- Do not teach raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the
  preferred application column authoring pattern in active Tigrbl README
  examples. Why: readers would treat storage lowering targets as the primary
  Tigrbl field contract.
- Do not show direct DB/session transaction calls in application snippets. Why:
  snippets should teach lifecycle-owned transaction progression, not local
  session mutation.

Avoid:

- Avoid terse README guidance that only says "use Tigrbl". Readers should see
  what to do, what not to do, and which exceptions belong to lower-level
  implementation surfaces. Why: without the reason and boundary, "use Tigrbl"
  is too vague to prevent framework, ORM, transport, and lifecycle drift.
