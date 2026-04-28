# AppSpec and RouterSpec composition proof

Run date: 2026-04-27

Commands:

- `.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_tests/v4/tests/spec/test_master_app_spec_surface.py pkgs/core/tigrbl_tests/v4/tests/spec/test_spec_export_surface.py pkgs/core/tigrbl_tests/v4/tests/spec/test_appspec_routerspec_contract.py pkgs/core/tigrbl_tests/v4/tests/spec/test_table_column_spec_contract.py pkgs/core/tigrbl_tests/v4/tests/spec/test_opspec_response_contract.py -q`
- `.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_core/tests/test_app_spec.py pkgs/core/tigrbl_core/tests/test_router_spec.py pkgs/core/tigrbl_core/tests/test_nested_specs_only.py pkgs/core/tigrbl_core/tests/test_spec_serde.py -q`

Results:

- V4 AppSpec, RouterSpec, table, column, op, response, and export contracts: 22 passed.
- Core AppSpec, RouterSpec, nested spec, and serde regression slice: 17 passed.

Certification decision:

- `feat:appspec-contract-001` is implemented for the governed AppSpec contract surface.
- `feat:routerspec-contract-001` is implemented for the governed RouterSpec contract surface.
- `feat:appspec-routerspec-composition-001` is implemented for nested RouterSpec composition with router-owned TableSpec values and typed metadata.
- Existing claim `clm:appspec-routerspec-composition-contract-001` remains evidenced at T2 and linked to passing tests plus passed evidence.
