# Authoring BCP

This document defines the best current practice for application-facing Tigrbl
authoring. It is a developer guide over the governed SSOT and package
boundaries; it does not replace `.ssot/` ADRs, specs, claim records, or release
evidence.

The short rule is: application code should describe service behavior through
Tigrbl-owned authoring surfaces, and lower-level packages should hide ASGI,
SQLAlchemy, runtime, and engine mechanics behind Tigrbl contracts.

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
  documentation surfaces.
- Do model a domain behavior once and let Tigrbl project it into REST,
  JSON-RPC, OpenAPI, OpenRPC, diagnostics, schemas, and runtime plans.
- Do keep transport-specific behavior behind Tigrbl bindings, runtime atoms,
  concrete adapters, or engine/plugin boundaries.
- Do use Tigrbl diagnostics such as `/system/methodz`, `/system/hookz`, and
  `/system/kernelz` when checking what the framework actually registered.

Do not:

- Do not author application endpoints with FastAPI `FastAPI`, `APIRouter`,
  dependency wiring, route decorators, middleware registration, or lifecycle
  hooks.
- Do not author application endpoints with Starlette route, request, response,
  middleware, background-task, or lifecycle classes.
- Do not author application endpoints with Flask `Flask`, `Blueprint`, route
  decorators, request/response globals, `MethodView`, extension registration,
  or lifecycle hooks.
- Do not wrap Tigrbl model behavior in transport-specific route handlers when
  an operation spec can represent the behavior.
- Do not use FastAPI or Starlette documentation generation as the source of
  truth for a Tigrbl surface.

Avoid:

- Avoid treating ASGI as the author-facing API. ASGI is the runtime protocol
  boundary; Tigrbl is the authoring boundary.
- Avoid adding one-off route wrappers that drift from the operation inventory.
- Avoid transport-only shortcuts that make REST, JSON-RPC, docs, diagnostics,
  and hooks disagree about what the service supports.

## Spec-First Table And Column Authoring

Do:

- Do express field behavior through Tigrbl table, column, datatype, storage,
  IO, request, response, and operation specs.
- Do use Tigrbl column helpers and `ColumnSpec`-backed metadata when a field
  belongs to a Tigrbl model.
- Do keep storage intent, wire-schema intent, validation intent, defaulting,
  masking, ownership, tenancy, and operation visibility in specs that the
  schema/runtime/docs layers can read.
- Do let Tigrbl lower column intent into SQLAlchemy, Pydantic, engine-specific
  datatypes, runtime schemas, and documentation projections.

Do not:

- Do not use raw SQLAlchemy `mapped_column(...)` as the primary application
  authoring surface when Tigrbl specs can express the column behavior.
- Do not use raw SQLAlchemy `Column(...)` as the primary application authoring
  surface when Tigrbl column helpers or specs can express the column behavior.
- Do not attach live sessions, request objects, transport handles, or engine
  instances to core specs.
- Do not mutate compiled specs in place after runtime plans have been built.

Avoid:

- Avoid duplicating the same field rules in SQLAlchemy, Pydantic, docs, and
  request handlers. Put the reusable rule in the Tigrbl spec layer.
- Avoid treating ORM materialization as the source of truth. SQLAlchemy is a
  lowering target for storage and inspection; Tigrbl specs are the authoring
  contract.
- Avoid hand-written Pydantic envelopes for payloads that belong to a Tigrbl
  operation; use `get_schema(...)` and schema helpers.

## Operation, Handler, And Lifecycle Dispatch

Do:

- Do model domain verbs as canonical operations, operation-pack verbs, or
  explicit custom `OpSpec` entries.
- Do put policy, validation, enrichment, audit, and response shaping in hooks
  attached to the relevant phase.
- Do use Tigrbl handlers through operation specs and kernel/runtime dispatch so
  REST, JSON-RPC, schemas, docs, hooks, and diagnostics stay aligned.
- Do bind engines declaratively at app, router, table, or operation scope.
- Do let runtime phases own transaction progression: `START_TX`,
  `PRE_HANDLER`, `HANDLER`, `POST_HANDLER`, `PRE_COMMIT`, `TX_COMMIT`,
  `POST_COMMIT`, and rollback/error phases.

Do not:

- Do not call database direct methods such as `flush()` or `commit()` from
  application hooks or handlers.
- Do not construct ad-hoc SQLAlchemy engines, sessions, or sessionmakers inside
  request handlers.
- Do not bypass kernel/runtime plans when wiring REST or JSON-RPC handlers.
- Do not implement core persistence, transport emission, or transaction
  lifecycle by hand in user hooks.
- Do not make route handlers the canonical business-logic surface when a Tigrbl
  handler or operation spec can represent the behavior.

Avoid:

- Avoid direct DB/session mutation from application code. Put persistence
  semantics behind operations, handlers, atoms, engine adapters, and lifecycle
  phases.
- Avoid hiding behavior in route wrappers or ad-hoc dependencies that
  diagnostics cannot see.
- Avoid adding operation-specific policy at the transport layer when the same
  rule belongs in specs, hooks, or lifecycle phases.

## Allowed Exceptions

The following uses are allowed when they are explicit about their boundary:

- Framework internals may use ASGI-compatible or Starlette-compatible behavior
  behind Tigrbl-owned concrete adapters.
- Engine packages may use SQLAlchemy to implement engine, session, transaction,
  storage, reflection, and datatype-lowering behavior.
- Base/concrete internals may lower `ColumnSpec` and related metadata into
  SQLAlchemy constructs.
- Tests, examples, and benchmarks may use FastAPI, Starlette, Flask,
  SQLAlchemy `Column(...)`, or SQLAlchemy `mapped_column(...)` when they are
  validating compatibility, parity, legacy behavior, migration behavior, or
  lower-level framework boundaries.
- Deprecated and archived docs may preserve historical examples, but they are
  not current authoring guidance.

When an exception is used, the code or README should make the boundary clear:
benchmark, test fixture, migration compatibility, engine adapter, concrete
adapter, or framework-internal lowering.

## README And Example Requirements

Do:

- Do make public README examples use Tigrbl facade imports and Tigrbl-owned
  authoring surfaces.
- Do describe exceptions plainly when an example intentionally shows a lower
  layer, benchmark, test fixture, or compatibility path.
- Do keep detailed BCP guidance in this file, the repository README, and the
  facade package README.

Do not:

- Do not teach FastAPI or Starlette route authoring as an application pattern in
  active Tigrbl README examples.
- Do not teach Flask route, blueprint, or `MethodView` authoring as an
  application pattern in active Tigrbl README examples.
- Do not teach raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the
  preferred application column authoring pattern in active Tigrbl README
  examples.
- Do not show direct DB/session transaction calls in application snippets.

Avoid:

- Avoid terse README guidance that only says "use Tigrbl". Readers should see
  what to do, what not to do, and which exceptions belong to lower-level
  implementation surfaces.
