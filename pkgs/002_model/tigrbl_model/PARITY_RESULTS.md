# Parity verification results

Verified on 2026-07-16 before any Tigrbl package migration.

## Result

The bounded contract in `PARITY.md` passes. Pydantic 2.13.3 was used only as
the differential-test oracle; the built `tigrbl_model` wheel imports and runs
in an isolated environment where Pydantic is absent.

| Check | Result |
|---|---|
| Python 3.12 package suite | 56 passed |
| Python 3.13 package suite | 56 passed |
| Python 3.14 package suite | 56 passed |
| Ruff | passed |
| Wheel build | passed |
| Source distribution build | passed |
| Standalone wheel smoke test | passed; `pydantic=absent` |

Python 3.10 and 3.11 were not installed in the verification environment, so
they were not executed locally. The package declares both versions and uses
compatibility dependencies for `tomllib` and `typing.Self` on Python 3.10.

## Evidence groups

- Unit tests cover model construction, fields, configuration, validation,
  validators, errors, rebuilding, copying, and construction without validation.
- Serialization tests cover JSON, YAML, TOML, legacy aliases, plain dataclasses,
  and the four-mixin aggregation contract.
- Differential tests compare the supported surface directly with Pydantic v2.
- JSON Schema tests cover constraints, aliases, nested references, roots,
  extras, and custom reference templates.
- Contract tests cover dynamic models and patterns used by first-party Tigrbl.
- The usage-inventory test scans first-party runtime imports, method calls, and
  keyword arguments, including the used `pydantic_core` and `ConfigDict`
  surfaces, so an uncatalogued Pydantic dependency fails the suite.

## Repository-level note

The workspace package-governance test currently expects 42 package roots while
this worktree contains 47. That pre-existing count mismatch prevents the whole
governance test from passing. The new package independently contains every
legal file, badge, Python-version label, and README section enforced by that
test.
