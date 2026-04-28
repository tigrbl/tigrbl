# Package buildability and importability evidence

Run date: 2026-04-27

Commands:

- `.venv\Scripts\python.exe -m pytest tools/ci/tests/test_packages_buildable_importable.py -q`
- `.venv\Scripts\python.exe -m pytest pkgs\apps\tigrbl_spiffe\tests\test_imports.py -q`
- `.venv\Scripts\python.exe -m pytest tools/ci/tests/test_packages_buildable_importable.py pkgs\apps\tigrbl_spiffe\tests\test_imports.py -q`

Results:

- Package buildability/importability gate: 1 passed, 1 warning.
- SPIFFE import smoke: 1 passed.
- Combined package gate plus SPIFFE import smoke: 2 passed, 1 warning.

Repairs made:

- Restored the `tigrbl.session` compatibility surface for engine packages that still import `tigrbl.session`, `tigrbl.session.base`, or `tigrbl.session.spec`.
- Restored public `include_model`, `include_table`, and `include_models` facade exports alongside `include_tables`.
- Removed the import-time circular dependency from `tigrbl_engine_dataframe`.
- Updated SPIFFE table modules to import `HTTPException` from the public `tigrbl` facade while retaining compatibility with local test stubs.
- Hardened the package importability gate against unspecced test stubs left in `sys.modules` by neighboring tests.

Certification decision:

The explicit package buildability and importability feature has executable passing evidence for the active package tree. Remaining active-line blockers are outside this explicit package-importability feature.
