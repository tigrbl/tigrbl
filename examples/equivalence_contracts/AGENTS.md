# Agent Guide: Equivalence Contracts

This directory contains local, uv-based equivalence demonstrations for Tigrbl,
FastAPI, Flask, and future vendor/framework comparisons. These examples are
not packaging artifacts for PyPI. They are executable technical-marketing proof:
developers should be able to read the files, understand the authoring style,
run the tests, and see the asserted parity.

## Purpose

Each equivalence demonstrates that a Tigrbl-first implementation can express the
same externally observable behavior as familiar vendor/framework code while
using Tigrbl's first-class authoring surface.

The goal is not only test parity. The goal is readable, certifiable pedagogy:

- show the developer intent;
- show one idiomatic implementation per vendor/framework;
- start real servers with shared runtime code;
- call those servers with one shared client assertion path;
- assert the exact outputs that prove the equivalence.

## Non-Negotiable Pattern

Every equivalence must have four parts:

1. **Contract/catalog entry** in `src/tigrbl_equivalence_contracts/contracts.py`.
2. **Vendor implementations** inside that equivalence's own folder.
3. **Runtime proof code** inside that equivalence's own folder.
4. **Pytest coverage** under `tests/` that certifies the matrix entry and asserts
   the expected evidence.

If any of the four parts is missing, the equivalence is incomplete.

## Current Reference Shape

Use the Widget REST CRUD equivalence as the reference style:

- `equivalences/rest_crud_widget/tigrbl_impl.py` defines a `Widget`
  `RestTable` and module-level `app`.
- `equivalences/rest_crud_widget/fastapi_impl.py` defines the SQLAlchemy row,
  Pydantic models, FastAPI routes, and module-level `app`.
- `equivalences/rest_crud_widget/flask_impl.py` defines the SQLAlchemy row,
  Flask routes, and module-level `app`.
- `equivalences/rest_crud_widget/runtime.py` owns the equivalence-specific
  `httpx` client assertion sequence.
- `equivalences/rest_crud_widget/contract.py` maps each framework app to its
  runtime proof.
- Top-level `contracts.py` only aggregates per-equivalence contracts.
- `tests/test_certifiable_equivalences.py` asserts certification, matrix rows,
  and expected evidence.

## Implementation Style

Vendor implementation files must read like normal framework examples. A
developer should be able to open one file and see the app they would actually
write in that framework.

Do:

- Use module-level app objects.
- Use the framework's normal first-class exports and idioms.
- Keep Tigrbl examples pro-Tigrbl and direct: use Tigrbl table/app primitives.
- Keep FastAPI examples recognizably FastAPI: decorators, Pydantic models,
  SQLAlchemy where persistence is needed.
- Keep Flask examples recognizably Flask: decorators, request/jsonify, SQLAlchemy
  where persistence is needed.
- Use SQLite for local persistence demonstrations unless the equivalence is
  explicitly about another engine.
- Keep shared mechanics in runtime modules: port selection, server startup,
  readiness polling, shutdown, client calls, and repeated expected evidence.
- Use asserts, not prints, to demonstrate expected behavior.
- Prefer module-level docstrings, class docstrings, method/function docstrings,
  and selective inline comments to explain the lesson.

Do not:

- Add app factories, router factories, helper builders, projection helpers, or
  abstract wrappers to make the examples shorter.
- Hide framework authoring behind shared abstractions.
- Put `start_server()` or repeated server lifecycle code in vendor implementation
  files.
- Duplicate the same `httpx` client call sequence in every vendor file.
- Use test clients or in-process transports when the equivalence requires real
  client-to-server behavior.
- Use `print()` as proof.
- Use nonlocal engines, bridges, or dialect abstractions for simple SQLite
  examples.
- Add equivalence rows that are not backed by runnable implementations and
  tests.

## Documentation Style

These files are instructional code. Write them as if a developer is learning why
the Tigrbl implementation is simpler while still behaviorally equivalent.

Use:

- module-level docstrings to explain the role of a file;
- dataclass/class docstrings to explain the object in the equivalence system;
- method/function docstrings to explain what a callable proves;
- inline comments only where a reader benefits from local context.

Avoid comments that merely restate code. Comments should explain why the shape
matters for equivalence, pedagogy, or certification.

## Directory Organization

Every equivalence gets its own directory:

```text
examples/equivalence_contracts/
  AGENTS.md
  pyproject.toml
  README.md
  src/tigrbl_equivalence_contracts/
    contracts.py
    runtime.py
    equivalences/
      rest_crud_widget/
        contract.py
        runtime.py
        tigrbl_impl.py
        fastapi_impl.py
        flask_impl.py
      table_base/
        contract.py
        runtime.py
        tigrbl_impl.py
        fastapi_impl.py
        flask_impl.py
  tests/
    test_certifiable_equivalences.py
```

Do not add new equivalence implementation modules directly under shared
top-level folders. Shared top-level modules may contain only common mechanics
such as server lifecycle helpers and the aggregate matrix loader.

Use normalized directory names based on the equivalence ID:

```text
src/tigrbl_equivalence_contracts/
  contracts.py
  equivalences/
    rest_crud_widget/
      runtime.py
      tigrbl_impl.py
      fastapi_impl.py
      flask_impl.py
```

The matrix entry must remain the index. It should name the equivalence ID,
intent, claim, status, source documents, implementation code refs, and runtime
proof callable.

## Contract Rules

Contract entries should be small and declarative:

- Use stable IDs such as `rest-crud.widget`.
- Use intent text that describes the developer task.
- Use claims that are precise enough to test.
- Point `code_ref` fields at readable implementation files.
- Keep lazy imports so docs can render the matrix without importing optional
  runtime dependencies unnecessarily.

The contract should not become a framework abstraction layer. It is a catalog
and certification dispatcher.

## Runtime Rules

Runtime code owns common behavior:

- real local server startup;
- ASGI/WSGI server selection;
- port allocation;
- readiness polling;
- shutdown;
- shared `httpx` client calls;
- expected evidence constants;
- final parity assertions.

Runtime code may be a shared module when behavior is common across equivalences,
but every equivalence must still have its own `runtime.py` that names the
expected evidence and exposes the proof callable used by that equivalence's
contract.

## Test Rules

Every equivalence must have tests that:

- certify every declared matrix row;
- assert every implementation appears in the matrix;
- assert the expected evidence for the equivalence;
- fail if any vendor implementation diverges from the shared client proof.

Run these checks before committing equivalence work:

```powershell
uv run --project examples/equivalence_contracts --group dev python -m pytest -q examples/equivalence_contracts/tests
python tools/ci/validate_equivalence_runtime_contracts.py
python tools/docs/update_equivalence_docs.py --check
git diff --check
```

## Change Discipline

Keep equivalence changes scoped. Do not mix unrelated Tigrbl runtime changes,
generated docs rewrites, or package lock churn into equivalence commits unless
the equivalence requires them.

When adding a new equivalence, update the matrix, implementation files, runtime
proof, and tests together in the same change. The result should be readable to a
human and certifiable by pytest.
