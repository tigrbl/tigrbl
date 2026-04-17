# ADR-1044: Next-target datatype/table program activation

﻿
Accepted.

## Decision

Activate the datatype/table architecture as the governed next-target program for the active line `0.3.19.dev1`.

The governed next-target program now includes:

- canonical datatype declarations via `DataTypeSpec`
- engine-agnostic storage intent via `StorageTypeRef`
- executable semantic behavior via `TypeAdapter` and `TypeRegistry`
- engine-owned lowering via `EngineTypeLowerer`, `EngineRegistry`, and `EngineDatatypeBridge`
- `ColumnSpec.datatype` integration and related spec cleanup
- multi-engine table portability and interoperability planning
- reflection-driven round-trip recovery planning

## Sequencing

1. semantic datatype core
2. engine bridge and lowering
3. column/field/storage integration
4. table program and portability rules
5. reflection and reverse mapping

## Rationale

The release `0.3.18` already closed its governed current-boundary target. The datatype/table program should therefore progress as isolated next-target work rather than as a silent extension of the frozen release claim set.

## Consequences

- next-target work is governed and named explicitly
- current-target certification remains honest and frozen
- the active dev line can absorb design and implementation changes without confusing them with the promoted release history
