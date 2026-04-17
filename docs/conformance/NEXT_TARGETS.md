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

### Scope sources already incorporated into the governed plan

The design direction now captured here and in the ADR set includes:

- semantic datatype declarations separated from Rust engine lowering
- engine registries and lowerers instead of adapter hardcoding
- `to_json`, `to_df`, `encode`, and `decode` as explicit adapter behaviors
- table/program sequencing after the datatype semantic center is in place

## Sequence for the next line

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

## Governing ADR set for the next target

- `.ssot/adr/ADR-1042-deferred-next-target-datatype-table-program.md`
- `.ssot/adr/ADR-1043-post-promotion-release-history-freeze.md`
- `.ssot/adr/ADR-1044-next-target-datatype-table-program-activation.md`

## Deliverables now established by Phase 14

- active dev line `0.3.19.dev1`
- active dev-bundle scaffold `docs/conformance/dev/0.3.19.dev1/`
- next-target ADRs
- handoff audit note `docs/conformance/audit/2026/p14-post-promotion-handoff/README.md`
- archived promotion-only WIP note `docs/notes/archive/2026/p14-post-promotion-handoff/README.md`

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
