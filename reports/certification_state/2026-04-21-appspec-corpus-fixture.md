# AppSpec Corpus Fixture Certification Projection (2026-04-21)

## Purpose

This projection records execution evidence for the canonical and negative AppSpec corpus fixture lanes.  
Canonical source fixtures live under `pkgs/core/tigrbl_tests/tests/fixtures/` and this report is a derived projection.

## Fixture Artifacts

- `pkgs/core/tigrbl_tests/tests/fixtures/appspec_corpus.canonical.json`
- `pkgs/core/tigrbl_tests/tests/fixtures/appspec_corpus.negative.json`

## Executed Test Lanes

Command:

```bash
.\.venv\Scripts\python.exe -m pytest -q \
  pkgs/core/tigrbl_tests/tests/harness/test_04_appspec_corpus_fixture.py \
  pkgs/core/tigrbl_tests/tests/harness_e2e/test_01_appspec_corpus_uvicorn.py
```

Result summary:

- `6 passed in 3.84s`
- Positive corpus lane validated fixture schema, stable IDs, and AppSpec RPC mount behavior.
- E2E positive corpus lane validated REST/JSON-RPC roundtrip and parity visibility.
- Negative corpus lane validated fail-closed behavior for no-RPC-mount and unknown-RPC-method runtime dispatch.

## Governance Intent

This report is intended to back SSOT evidence rows for:

- canonical AppSpec corpus fixture support
- negative corpus fail-closed runtime behavior
