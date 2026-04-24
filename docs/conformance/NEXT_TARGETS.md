# Next Targets

## Status at handoff

Stable release `0.3.18` is frozen as current-boundary release history.

The active working-tree line is now `0.3.19.dev1`.

This line is governed as the next-target planning line. It is intentionally separated from the frozen current-target release bundle and does not reopen the already-closed `0.3.18` claim set.

## Planning rule

For `0.3.19.dev1`:

- use planning or implementation language only
- do **not** use Tier 3 certification wording
- do **not** edit the frozen `docs/conformance/releases/0.3.18/` bundle except for governed corrective maintenance
- keep the current-target boundary frozen while next-target work is still design/planning-only

## Active next-target program

The active next-target program is the datatype/table architecture that was previously deferred from the current-target certification cycle.

The active line also now carries a governed Transport-dispatch track inside the same next-target boundary.

### Program scope

The next-target plan now governs these items:

1. canonical datatype system as the active semantic center
2. `ColumnSpec.datatype` adoption across the framework
3. `DataTypeSpec`, `StorageTypeRef`, `TypeAdapter`, `BaseTypeAdapter`, and `TypeRegistry`
4. engine-owned lowering via `EngineTypeLowerer`, `EngineRegistry`, and `EngineDatatypeBridge`
5. reverse mapping and reflection via `ReflectedTypeMapper`
6. engine-wide datatype alignment for relational, dataframe, file, cache, and probabilistic engines
7. table-spec portability, multi-engine table semantics, and interoperability
8. reflection-driven round-trip schema recovery

### Transport-dispatch track

The transport-dispatch track now governs these items:

1. single-dispatch transport flow
2. removal of non-conforming transport bypasses
3. binding-driven REST and JSON-RPC ingress materialization
4. KernelPlan-owned lookup and matching
5. executor non-ownership for transport matching
6. endpoint-keyed JSON-RPC ingress identity
7. default endpoint mappings owned by `tigrbl_core`
8. REST/JSON-RPC semantic parity through one shared dispatch path

### Supported server boundary

The active line now also tracks the supported server boundary explicitly.

Supported server runners are limited to:

1. `tigrcorn`
2. `uvicorn`
3. `hypercorn`
4. `gunicorn`

The following remain tracked only as out-of-boundary server/runtime rows on the active line:

1. `daphne`
2. `twisted`
3. `granian`

Any other non-listed server/runtime adapters remain out of boundary until a new governed feature/claim row is added.

### Scope sources already incorporated into the governed plan

The design direction now captured here and in the ADR set includes:

- semantic datatype declarations separated from Rust engine lowering
- engine registries and lowerers instead of adapter hardcoding
- `to_json`, `to_df`, `encode`, and `decode` as explicit adapter behaviors
- table/program sequencing after the datatype semantic center is in place

## Sequence for the next line

### Stage T0 - Transport-dispatch governance setup

- install repo-local `ssot-registry 0.2.6`
- author ADR-1045 through ADR-1047
- author SPEC-2013 through SPEC-2016
- create transport-dispatch features, tests, claims, and evidence rows
- create and freeze boundary `bnd:transport-dispatch-track-001`


### Stage N1 — Semantic datatype core

- establish `DataTypeSpec` and `StorageTypeRef`
- finalize the `TypeAdapter` protocol and builtin adapters
- establish a governed registry contract
- keep adapters engine-agnostic

### Stage N2 — Engine bridge and lowering

- establish `EngineTypeLowerer`
- establish `EngineRegistry`
- establish `EngineDatatypeBridge`
- align SQLite, SQLAlchemy, and registered engines to the bridge contract

### Stage N3 — Column and field integration

- add `ColumnSpec.datatype`
- shrink `StorageSpec` back to storage policy
- align `FieldSpec`, `IOSpec`, and `ForeignKeySpec` to the canonical type surface
- patch `_materialize_colspecs_to_sqla()` and related paths

### Stage N4 — Table program

- introduce governed table-spec planning
- define portability/interoperability boundaries
- define engine-family expectations for relational, dataframe, file, cache, and index-like engines

### Stage N5 — Reflection and round-trip recovery

- add `ReflectedTypeMapper`
- define reflection/import behavior
- document best-effort vs metadata-preserving round-trip rules

### Stage T1 - Single-dispatch transport flow

- restore one transport-dispatch path through the kernel-owned plan
- keep concrete `/rpc` mounts as thin ingress adapters only
- move transport lookup and matching back into KernelPlan compilation and atoms
- preserve semantic parity without weakening parity tests

### Stage T2 - Supported server contract and OOB tracking

- keep the supported runner set locked to `tigrcorn`, `uvicorn`, `hypercorn`, and `gunicorn`
- track each supported runner as its own governed feature on the active line
- keep `daphne`, `twisted`, and `granian` tracked only as out-of-boundary rows
- treat any other non-listed server/runtime adapter as out of boundary until separately governed

## Governing ADR set for the next target

- `.ssot/adr/ADR-1042-deferred-next-target-datatype-table-program.yaml`
- `.ssot/adr/ADR-1043-post-promotion-release-history-freeze.yaml`
- `.ssot/adr/ADR-1044-next-target-datatype-table-program-activation.yaml`
- `.ssot/adr/ADR-1045-transport-dispatch-track-boundary-and-sequencing.yaml`
- `.ssot/adr/ADR-1046-endpoint-keyed-multiplexed-transport-bindings.yaml`
- `.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.yaml`

## Deliverables now established by Post-promotion handoff

- active dev line `0.3.19.dev1`
- active dev-bundle scaffold `docs/conformance/dev/0.3.19.dev1/`
- next-target ADRs
- handoff audit note `docs/conformance/audit/2026/post-promotion-handoff/README.md`
- archived promotion-only WIP note `docs/notes/archive/2026/post-promotion-handoff/README.md`
- transport-dispatch setup note `.ssot/reports/transport-dispatch-track-setup.md`
- transport-dispatch boundary snapshot `.ssot/releases/boundaries/bnd_transport-dispatch-track-001.snapshot.json`

## Non-goals for this checkpoint

This checkpoint does **not** claim that the next-target datatype/table program is implemented.

It does **not**:

- promote a new stable release
- reopen the frozen current target
- widen the `0.3.18` certification boundary
- claim external validation

## Exit condition for the handoff itself

The handoff is considered complete when all of the following are true:

- current target is frozen as release history
- active next-line version is opened in package metadata and docs
- next-target work is isolated and governed
- resolved promotion-only WIP notes are archived
- the repository can be read top-down without mixing `0.3.18` release history with `0.3.19.dev1` planning work
