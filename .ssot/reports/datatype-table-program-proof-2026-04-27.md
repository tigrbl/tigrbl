# Datatype and table program proof

Run date: 2026-04-27

Commands:

- `.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_core/tests/test_semantic_datatype_core.py pkgs/core/tigrbl_core/tests/test_column_datatype_integration.py pkgs/core/tigrbl_core/tests/test_adapter_registry_contract.py pkgs/core/tigrbl_core/tests/test_engine_bridge_lowering.py pkgs/core/tigrbl_core/tests/test_reflection_roundtrip_recovery.py pkgs/core/tigrbl_core/tests/test_engine_family_alignment.py pkgs/core/tigrbl_core/tests/test_table_portability_contract.py pkgs/core/tigrbl_core/tests/test_schema_roundtrip_recovery.py -q`
- `.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_base/tests/test_column_datatype_lowering.py -q`
- `cargo test -p tigrbl_rs_spec --test spec_contract`

Results:

- Core datatype, adapter registry, engine bridge, reflection, portability, and schema recovery contracts: 35 passed.
- Base ColumnSpec datatype lowering contract: 1 passed.
- Rust spec datatype and engine bridge contract: 9 passed.

Certification decision:

- The canonical datatype catalog and semantic center are implemented.
- ColumnSpec datatype attachment is implemented across core and base surfaces.
- The datatype adapter registry and engine lowering bridge are implemented.
- Reflected datatype reverse mapping and schema reflection recovery are implemented.
- Default engine-family datatype alignment and multi-engine table portability are implemented for the governed active-line contract tests.
