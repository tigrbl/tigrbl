# Proposal Draft: LTAP Table Profile for Tigrbl

Status: proposal draft

This draft is not an accepted ADR, SPEC, feature row, implementation contract,
or release claim. It defines a concrete shape for discussing an LTAP table in
Tigrbl without treating LTAP support as implemented. The current repo already
has built-in table profiles for OLTP, OLAP, bulk CRUD, realtime, streaming,
SSE, WebSocket, and WebTransport surfaces. It does not currently define a
built-in LTAP table profile or lake-maintenance operation family.

## Problem

Tigrbl already separates table intent from transport projection:

- `TableProfileSpec` selects canonical operation targets and default binding
  families.
- `OpSpec` owns each public operation contract, including `target`, `alias`,
  bindings, `tx_scope`, schemas, hooks, handlers, engine routing, and `extra`.
- `SessionSpec` carries backend-agnostic transaction, timeout, consistency,
  resource, observability, cache, and data-protection policy.
- `EngineSpec.supports()` exposes engine capability dictionaries for portable
  checks and fail-closed behavior.

LTAP should build on those surfaces. It should not become a hidden atom family,
an overloaded OLTP table, or a generic lakehouse marketing label. In Tigrbl,
LTAP should mean: a table profile that combines row-serving operations,
analytical query operations, and explicitly declared maintenance operations
against engines that can state whether they support the required semantics.

## Current Baseline

The live `TableProfileSpec` registry has separate built-ins for OLTP and OLAP:

| Current profile | Selected operation targets |
| --- | --- |
| `oltp`, `rest_oltp`, `jsonrpc_oltp`, `rest_jsonrpc_oltp` | `create`, `read`, `update`, `replace`, `merge`, `delete`, `list`, `count`, `exists` |
| `olap`, `rest_olap`, `jsonrpc_olap`, `rest_jsonrpc_olap` | `read`, `list`, `count`, `exists`, `aggregate`, `group_by` |
| `rest_bulk_crud`, `jsonrpc_bulk_crud` | `create`, `read`, `update`, `replace`, `delete`, `list`, `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_delete` |
| realtime and stream profiles | `publish`, `subscribe`, `tail`, `upload`, `download`, `append_chunk`, `send_datagram`, `checkpoint` depending on transport profile |

`OpSpec.TargetOp` currently includes CRUD, bulk CRUD, analytical query,
realtime/streaming, `checkpoint`, and `custom`. It does not include
`optimize`, `compact`, `vacuum`, `snapshot`, `expire_snapshots`,
`rewrite_manifests`, `ingest_file`, or other lake-maintenance verbs as
first-class targets.

## Proposed Table Shape

An LTAP table should be modeled first as a custom profile over existing
operation surfaces, then promoted only if implementation and SSOT governance
accept it.

```python
LTAP_TABLE_PROFILE = TableProfileSpec(
    kind="ltap",
    role="concrete",
    docs_exposure="default",
    runtime_exposure="declared",
    custom=True,
    namespace="tigrbl.proposals",
    ops=(
        make_profile_op("create"),
        make_profile_op("read"),
        make_profile_op("update"),
        make_profile_op("replace"),
        make_profile_op("merge"),
        make_profile_op("delete"),
        make_profile_op("list"),
        make_profile_op("count"),
        make_profile_op("exists"),
        make_profile_op("bulk_create"),
        make_profile_op("bulk_update"),
        make_profile_op("bulk_replace"),
        make_profile_op("bulk_merge"),
        make_profile_op("bulk_delete"),
        make_profile_op("aggregate"),
        make_profile_op("group_by"),
        make_profile_op("checkpoint"),
        OpSpec(
            alias="optimize",
            target="custom",
            arity="collection",
            tx_scope="none",
            persist="skip",
            extra={"ltap": {"kind": "maintenance", "action": "optimize"}},
        ),
        OpSpec(
            alias="snapshot",
            target="custom",
            arity="collection",
            tx_scope="read_only",
            persist="skip",
            extra={"ltap": {"kind": "metadata", "action": "snapshot"}},
        ),
    ),
)
```

This example is intentionally proposal-only. The important part is not the
exact Python spelling; it is the contract boundary:

- row-serving operations stay on normal canonical operation targets
- analytical queries stay on `aggregate` and `group_by`
- maintenance and lake-metadata actions are explicit `custom` ops until Tigrbl
  accepts first-class lake targets
- execution risk metadata lives in `OpSpec.extra` or future op-level fields,
  not in atoms

## Operation Families

LTAP needs three operation families. Only the first two are already first-class
canonical families.

| Family | Current targets | LTAP role |
| --- | --- | --- |
| Row-serving | `create`, `read`, `update`, `replace`, `merge`, `delete`, `list`, `count`, `exists`, bulk CRUD targets | Serves OLTP-style reads and writes against the current table state. |
| Analytical query | `aggregate`, `group_by`, `count`, `exists`, `list`, `read` | Serves OLAP-style scans, grouped reads, and point-in-time query shapes. |
| Maintenance and metadata | `checkpoint`, `custom` today | Coordinates snapshots, compaction, clustering, manifest rewrite, retention, statistics refresh, and metadata inspection. |

If LTAP graduates from proposal to implementation, the minimum new first-class
targets should be narrow and maintenance-oriented:

| Proposed target | Purpose | Why not use existing OLTP/OLAP target |
| --- | --- | --- |
| `optimize` | Engine-level layout optimization, clustering, compaction, or file rewrite. | It is not a row mutation and may rewrite physical layout without changing logical rows. |
| `snapshot` | Return current snapshot or version metadata. | It is table metadata, not a row read. |
| `expire_snapshots` | Apply retention policy to historical snapshots. | It changes table history/metadata, not current rows. |
| `refresh_stats` | Refresh engine-side statistics or metadata caches. | It supports planning and scheduling rather than user data semantics. |

Other verbs should remain `custom` until a concrete engine proves a portable
contract. Examples: `rewrite_manifests`, `vacuum`, `z_order`, `cluster`,
`ingest_file`, `replace_partitions`, and `rollback_to_snapshot`.

## Lifecycle Semantics Beyond OLTP and OLAP

OLTP operations are usually short, transactional, and row-oriented. OLAP
operations are usually read-heavy and scan-oriented. LTAP needs additional
lifecycle semantics because one table may mix foreground row traffic with
background or operator-driven maintenance.

### 1. Foreground Versus Maintenance Class

Every LTAP op should identify whether it is foreground serving, analytical
query, metadata inspection, or maintenance:

```python
extra={
    "ltap": {
        "class": "maintenance",
        "action": "optimize",
        "foreground_safe": False,
    }
}
```

This lets planners and operators reason about scheduling without embedding
policy in atom names.

### 2. Concurrency and Blocking Policy

LTAP ops need a scheduling signal for how they interact with concurrent
serving traffic:

```python
extra={
    "ltap": {
        "tx_block_policy": "allow_reads_block_writes",
        "lock_level": "table_metadata",
        "estimated_cost": "high",
    }
}
```

These fields are not correctness guarantees by themselves. They are scheduling
and blast-radius metadata that engines and runtimes can validate against
capability dictionaries.

### 3. Atomicity and Rollback Expectations

Some lake operations are atomic metadata swaps; others are best-effort physical
maintenance. The public op should say which one it expects:

```python
extra={
    "ltap": {
        "atomicity": "metadata_commit",
        "rollback": "snapshot_reference",
    }
}
```

Candidate values:

| Field | Candidate values |
| --- | --- |
| `atomicity` | `row_tx`, `metadata_commit`, `idempotent_best_effort`, `none` |
| `rollback` | `transaction`, `snapshot_reference`, `compensating_op`, `none` |

### 4. Point-in-Time Query Coordinates

LTAP should use `SessionSpec` for consistency coordinates where possible:

- `as_of_ts`
- `min_lsn`
- `consistency`
- `staleness_ms`
- `page_snapshot`

If snapshot IDs become first-class, they should be added to session/query
policy deliberately rather than hidden in handler-specific payloads.

### 5. Observable Maintenance State

Long-running maintenance should not pretend to be ordinary synchronous CRUD.
An LTAP maintenance op can remain request-response only when the engine can
finish within bounded request limits. Otherwise it should return an operation
handle, emit status through a separate op, or bind to an accepted streaming
surface.

Initial proposal:

| Maintenance shape | Suggested Tigrbl surface |
| --- | --- |
| Fast metadata inspection | `custom` op with request-response binding |
| Bounded maintenance command | `custom` op returning status payload |
| Long-running maintenance | explicit job/status proposal, not in scope here |
| Continuous table change stream | existing realtime/stream `tail` or `subscribe`, not an LTAP-only feature |

## Engine Capability Mapping

LTAP should be enabled by engine capabilities, not by table class naming alone.
`EngineSpec.supports()` is the right discovery surface because it already
returns capability dictionaries and can delegate to external engine
registrations.

Suggested capability keys:

| Capability key | Meaning |
| --- | --- |
| `transactional` | Engine can enforce transactional writes for row-serving ops. |
| `read_only_enforced` | Engine can enforce read-only sessions. |
| `isolation_levels` | Engine-supported transaction isolation levels. |
| `ltap` | Engine advertises LTAP-aware behavior. |
| `ltap.table_formats` | Supported table formats, such as `iceberg`, `delta`, `hudi`, or `native`. |
| `ltap.snapshot_reads` | Engine can read a stable snapshot or version. |
| `ltap.metadata_commits` | Engine can apply atomic metadata commits. |
| `ltap.concurrent_read_write` | Engine can run reads and writes concurrently under documented semantics. |
| `ltap.maintenance_ops` | Supported maintenance actions. |
| `ltap.long_running_ops` | Maintenance actions that may outlive a request. |
| `ltap.stats_refresh` | Engine can refresh optimizer/statistics metadata. |

Example:

```python
{
    "engine": "duckdb",
    "transactional": True,
    "read_only_enforced": True,
    "isolation_levels": {"snapshot"},
    "ltap": {
        "table_formats": {"iceberg"},
        "snapshot_reads": True,
        "metadata_commits": False,
        "concurrent_read_write": "single_writer",
        "maintenance_ops": {"snapshot", "refresh_stats"},
        "long_running_ops": set(),
        "stats_refresh": True,
    },
}
```

Portable lowering rule:

1. Collect the table's `OpSpec` entries.
2. Read the effective `EngineSpec` from op, table, router, or app scope.
3. Call `EngineSpec.supports()`.
4. Validate every LTAP-tagged op against `ltap.*` capabilities.
5. Fail closed when a required capability is absent or ambiguous.

## Proposed Validation Rules

An LTAP table proposal should be rejected or downgraded when:

- it declares maintenance ops without `extra["ltap"]` metadata
- it declares foreground row mutations against an engine that is not
  transactional enough for the chosen `tx_scope`
- it declares point-in-time reads but the engine lacks snapshot-read capability
- it declares metadata commits but the engine cannot state atomicity behavior
- it binds long-running maintenance only as ordinary request-response without a
  bounded execution claim
- it mixes physical maintenance policy into atoms instead of keeping the public
  contract on `OpSpec` and engine capabilities

## What Stays Out Of Scope

This proposal does not add code or govern accepted support. It also does not
scope these items:

- a built-in `LtapTable` class
- new first-class `TargetOp` values
- SSOT ADR/SPEC/feature/claim/test/evidence rows
- an Iceberg, Delta Lake, Hudi, DuckDB, Spark, Trino, or ClickHouse engine
  implementation
- object-store credentials, catalog integrations, or metastore APIs
- background job orchestration for long-running maintenance
- distributed locking, leader election, or global scheduling
- table-format-specific optimization policies
- automatic conversion of OLTP tables into lakehouse tables
- treating all analytical engines as LTAP-capable

## Adoption Path

1. Keep this document proposal-only until there is a governed SSOT scope.
2. Prototype LTAP as custom `TableProfileSpec(kind="ltap", custom=True, ...)`
   in an experimental package or example.
3. Encode maintenance actions as explicit `custom` `OpSpec` rows with
   `extra["ltap"]` metadata.
4. Teach one engine registration to report narrow `ltap.*` capabilities.
5. Add validation that rejects unsupported LTAP ops before route/RPC/runtime
   exposure.
6. Only after those pieces work, decide whether to promote a small set of
   maintenance verbs into `TargetOp`.

## Open Questions

- Should `snapshot` be a first-class op target or a `SessionSpec` coordinate
  plus a metadata `custom` op?
- Should `optimize` be one portable verb, or should physical-layout actions
  remain engine-specific forever?
- Should long-running maintenance use a generic job/status surface shared with
  other Tigrbl operations?
- Should LTAP require both OLTP and OLAP operations, or is a table LTAP-capable
  when the engine can mix those workloads even if the profile selects only a
  subset?
- Should snapshot IDs live in `SessionSpec`, query payload schemas, or a future
  read-consistency spec?

## Addendum: Snapshot Resource and REST Shape

Dated: 2026-06-27

This addendum narrows the snapshot model toward a control-plane resource shape.
Snapshots should be exposed as table-like resources when callers need to list,
read, filter, aggregate, or act on snapshot metadata. Snapshot reads against the
data table should remain parameters on existing read/query operations.

### LTAP Data Table

Example resource: `Order` at `/orders`.

Proposed table operations:

```text
create
read
update
replace
merge
delete
list
count
exists
bulk_create
bulk_update
bulk_replace
bulk_merge
bulk_delete
aggregate
group_by
compact
analyze_stats
```

Snapshot reads are not separate table operations. They are query coordinates on
existing read/query operations:

```text
read(as_of_snapshot=...)
list(as_of_snapshot=...)
aggregate(as_of_snapshot=...)
group_by(as_of_snapshot=...)
```

Proposed `http.rest` paths:

```text
POST   /orders
GET    /orders
GET    /orders/{item_id}
PATCH  /orders/{item_id}
PUT    /orders/{item_id}
DELETE /orders/{item_id}

GET    /orders/_ops/count
GET    /orders/_ops/exists
POST   /orders/_ops/bulk_create
PATCH  /orders/_ops/bulk_update
PUT    /orders/_ops/bulk_replace
PATCH  /orders/_ops/bulk_merge
DELETE /orders/_ops/bulk_delete
POST   /orders/_ops/aggregate
POST   /orders/_ops/group_by

POST   /orders/_ops/compact
POST   /orders/_ops/analyze_stats
```

As-of examples:

```text
GET  /orders/{item_id}?as_of_snapshot=123
GET  /orders?as_of_snapshot=123
POST /orders/_ops/aggregate
POST /orders/_ops/group_by
```

### TableSnapshot Resource

Example control-plane path: `/tables/{table_id}/snapshots`.

`TableSnapshot` represents snapshot metadata, not a copied data table. It may be
materialized in Tigrbl, read through from an engine/catalog, or maintained as a
hybrid cache over backend snapshot truth.

Proposed snapshot operations:

```text
list
read
count
exists
aggregate
group_by
rollback
expire
```

Do not expose `create`, `update`, or `delete` initially. Snapshots should be
produced by backend commits, compaction, imports, or retention flows. Manual
snapshot-row mutation is a later control-plane design problem.

Proposed `http.rest` paths:

```text
GET  /tables/{table_id}/snapshots
GET  /tables/{table_id}/snapshots/{snapshot_id}

GET  /tables/{table_id}/snapshots/_ops/count
GET  /tables/{table_id}/snapshots/{snapshot_id}/_ops/exists
POST /tables/{table_id}/snapshots/_ops/aggregate
POST /tables/{table_id}/snapshots/_ops/group_by

POST /tables/{table_id}/snapshots/{snapshot_id}/_ops/rollback
POST /tables/{table_id}/snapshots/_ops/expire
```

The `/_ops/` segment is a proposed LTAP/control-plane REST convention for
non-CRUD actions. It avoids collisions with `{item_id}` and keeps action
semantics explicit.

Minimal new surface implied by this addendum:

```text
TableSnapshot.list
TableSnapshot.read
TableSnapshot.rollback
TableSnapshot.expire
```

Data tables get:

```text
as_of_snapshot on read/list/aggregate/group_by
compact
analyze_stats
```

`checkpoint` remains separate from snapshot semantics. A checkpoint is an
engine/runtime recovery or progress marker. A snapshot is a logical table
version or control-plane resource representing that version.
