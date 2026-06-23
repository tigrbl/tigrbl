# Engine and SQL Equivalence

This document compares Tigrbl engine and SQL authoring concepts to SQLAlchemy,
database dialects, and backend-specific engine plugins. It is a developer
translation guide. The governed source of truth remains SSOT entities, ADRs,
specs, and release evidence.

## Core Rule

Application code should bind storage behavior through Tigrbl-owned engine,
table, column, datatype, storage, operation, and lifecycle surfaces.

SQLAlchemy, database drivers, and backend clients are implementation substrates
behind Tigrbl engine adapters, datatype lowering, reflection, sessions,
transactions, tests, migrations, and benchmarks. They should not become the
primary application authoring contract when Tigrbl specs can express the
behavior.

## Engine Authoring Matrix

| Intent | Tigrbl surface | SQLAlchemy / raw framework analogue | Equivalence level | Notes |
|---|---|---|---|---|
| Engine declaration | `EngineSpec`, `engine_spec(...)`, engine decorators, app/router/table/op engine binding | `create_engine(...)`, async engine factories, driver DSNs | Analogous | Tigrbl keeps engine intent declarative and scope-aware. |
| Engine scope precedence | operation > table/model > router > app > defaults | Manual dependency wiring or session lookup | Tigrbl-specific | Resolution is part of the framework contract. |
| Session acquisition | Runtime session policy and engine provider | `Session`, `AsyncSession`, `sessionmaker` | Not equivalent | Tigrbl guards session lifecycle through runtime phases. |
| Transaction progression | Runtime phases such as `START_TX`, `PRE_COMMIT`, `TX_COMMIT`, rollback/error phases | Direct `flush()`, `commit()`, rollback calls | Not equivalent | Application hooks should not own transaction progression. |
| Field storage type | `DataTypeSpec`, `StorageSpec`, `StorageTypeRef` | SQLAlchemy column type or SQL dialect type | Projection-only | Physical type is a lowering target, not the authoring source. |
| Database reflection | `ReflectedTypeMapper`, engine adapters, metadata-preserving reflection modes | SQLAlchemy inspection and reflected metadata | Analogous | Reflected physical names are mapped back to canonical datatype hints. |
| Backend capability checks | `EngineSpec.supports()`, plugin capabilities | Dialect feature detection or driver docs | Analogous | Capability dictionaries should drive portable behavior and fail-closed decisions. |
| Backend plugin registration | `tigrbl-engine-*` packages and `register` entry points | Manually selected driver/package | Tigrbl-specific | Plugins own focused backend integration boundaries. |
| SQL query text | Engine/operation internals, migrations, tests, adapter code | Raw SQL strings or SQLAlchemy Core | Lower-layer only | Raw SQL can be valid behind the boundary, but should not define application operation semantics. |

## Engine Families

| Family | Tigrbl packages or kinds | Primary use | Equivalence notes |
|---|---|---|---|
| SQLite | `sqlite`, `tigrbl_engine_sqlite` | Local transactional storage, tests, small services | SQL syntax and locking behavior differ from Postgres. |
| PostgreSQL | `postgres`, `tigrbl_engine_postgres` | Production relational persistence | Strong relational target; isolation and JSON behavior remain backend-specific. |
| PostgreSQL/SQLite WAL | `tigrbl_engine_pgsqli_wal` | Transactional WAL workflows spanning Postgres and SQLite concerns | Treat as a focused engine plugin, not as generic dialect equivalence. |
| DuckDB | `tigrbl_engine_duckdb` | Embedded analytical database and OLAP workloads | SQL-compatible analytics surface with different transaction and concurrency traits. |
| BigQuery | `tigrbl_engine_bigquery` | BigQuery warehouse analytics | Warehouse SQL and job/session behavior differ from OLTP engines. |
| Snowflake | `tigrbl_engine_snowflake` | Snowflake warehouse analytics | Warehouse session semantics and SQL dialect behavior are backend-specific. |
| ClickHouse | `tigrbl_engine_clickhouse` | Analytical database workloads | Columnar analytics behavior is not OLTP equivalence. |
| DataFrame / Pandas / NumPy / PySpark | `dataframe`, `tigrbl_engine_dataframe`, `tigrbl_engine_pandas`, `tigrbl_engine_numpy`, `tigrbl_engine_pyspark` | In-process and distributed tabular workflows | DataFrame semantics are not SQL transaction semantics. |
| File-backed tabular | `tigrbl_engine_csv`, `tigrbl_engine_xlsx` | CSV and workbook-backed workflows | File storage is not equivalent to relational persistence. |
| Redis and cache-through | `tigrbl_engine_redis`, `tigrbl_engine_rediscachethrough` | Redis-backed data structures and cache-through workflows | Cache/data-structure semantics differ from SQL rows and transactions. |
| In-memory engines | `tigrbl_engine_inmemory`, `tigrbl_engine_inmemcache`, `tigrbl_engine_memkv`, `tigrbl_engine_memqueue`, `tigrbl_engine_mempubsub`, related memory plugins | Local tests, queues, pub/sub, rate, bloom, dedupe, and cache workflows | Useful for specific runtime behavior, not a SQL dialect substitute. |

## Datatype Lowering Matrix

Tigrbl starts from canonical logical datatypes. Physical names are lowering
targets for engine families.

| Logical datatype | SQLite | Postgres | DataFrame | File | Cache |
|---|---|---|---|---|---|
| `string` | `TEXT` | `TEXT` | `string` | `string` | `string` |
| `integer` | `INTEGER` | `BIGINT` | `int64` | `integer` | `string` |
| `number` | `REAL` | `DOUBLE PRECISION` | `float64` | `number` | `string` |
| `decimal` | `NUMERIC` | `NUMERIC` | `object` | `decimal` | `string` |
| `boolean` | `BOOLEAN` | `BOOLEAN` | `bool` | `boolean` | `string` |
| `bytes` | `BLOB` | `BYTEA` | `bytes` | `bytes` | `bytes` |
| `date` | `DATE` | `DATE` | `datetime64[ns]` | `date` | Not in built-in cache mapping |
| `datetime` | `DATETIME` | `TIMESTAMPTZ` | `datetime64[ns]` | `datetime` | Not in built-in cache mapping |
| `time` | `TIME` | `TIME` | `object` | `time` | Not in built-in cache mapping |
| `duration` | `TEXT` | `INTERVAL` | `timedelta64[ns]` | `duration` | Not in built-in cache mapping |
| `json` | `JSON` | `JSONB` | `object` | `json` | `json` |
| `object` | `JSON` | `JSONB` | `object` | `json` | `json` |
| `array` | `JSON` | `JSONB` | `object` | `json` | `json` |
| `uuid` | `TEXT` | `UUID` | `string` | `string` | `string` |
| `ulid` | `TEXT` | `UUID` | `string` | `string` | `string` |

This matrix is not a promise that every backend has identical comparison,
indexing, constraint, JSON-path, timezone, binary, or precision behavior. Those
differences belong to engine capabilities, adapters, migrations, and tests.

## Reflection Equivalence

Reflection maps physical engine metadata back into canonical datatype hints
where possible.

| Reflected physical name | Generic hint | SQLite hint | Postgres hint |
|---|---|---|---|
| `text` / `varchar` / `string` | `string` | `string` for `text` | `string` for `text` |
| `integer` / `int` / `bigint` | `integer` | `integer` for `integer` | `integer` for `bigint` |
| `float` / `double` / `real` | `number` | `number` for `real` | `number` for `double precision` |
| `numeric` / `decimal` | `decimal` | `decimal` for `numeric` | `decimal` for `numeric` |
| `json` / `jsonb` | `json` | `json` for `json` | `json` for `jsonb` |
| `uuid` | `uuid` | no engine-specific override | `uuid` for `uuid` |
| `blob` / `bytea` | `bytes` | `bytes` for `blob` | `bytes` for `bytea` |
| `timestamp` / `datetime` / `timestamptz` | `datetime` | `datetime` for `datetime` | `datetime` for `timestamptz` |
| `interval` | `duration` | no engine-specific override | `duration` for `interval` |

Reflection is best-effort unless strict mode is used. Unknown physical names
should not silently become portable semantic guarantees.

## SQL Non-Equivalence Rules

- Identical logical datatype names do not imply identical physical storage,
  precision, collation, timezone, indexing, or query behavior.
- JSON in SQLite, JSONB in Postgres, warehouse JSON variants, and DataFrame
  object columns are not interchangeable semantics.
- A SQLAlchemy `Column(...)` or `mapped_column(...)` is not the primary Tigrbl
  application authoring surface when `ColumnSpec` or column helpers can
  represent the field.
- Direct `flush()` and `commit()` calls in application hooks are not equivalent
  to Tigrbl runtime transaction phases.
- SQL text that works on one backend should not be documented as portable until
  engine-specific lowering or compatibility evidence exists.
- Cache, queue, pub/sub, bloom, dedupe, rate, and memory engines are engine
  integrations, not SQL dialect equivalents.

## Recommended Documentation Pattern

When documenting SQL or engine behavior, use this order:

1. State the Tigrbl semantic intent: operation, table, column, datatype,
   storage, engine, and lifecycle behavior.
2. State the declared engine scope and engine package, such as `sqlite`,
   `postgres`, `duckdb`, `bigquery`, `snowflake`, `redis`, or `dataframe`.
3. State the physical lowering or backend behavior when it matters.
4. State known non-equivalences and unsupported behavior.
5. Point to tests, adapters, or SSOT evidence for runtime support claims.

## Source Pointers

- `docs/developer/AUTHORING_BCP.md`
- `pkgs/core/tigrbl_core/tigrbl_core/_spec/engine_spec.py`
- `pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py`
- `pkgs/core/tigrbl_core/tigrbl_core/_spec/column_spec.py`
- `pkgs/core/tigrbl_core/tigrbl_core/_spec/storage_spec.py`
- `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/engine_resolver.py`
- `pkgs/engines/`
