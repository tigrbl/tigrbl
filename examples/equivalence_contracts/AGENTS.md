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

## Protocol Fidelity

The Tigrbl table/profile name is binding authority. Vendor/framework examples
must implement the same transport family and framing semantics that the Tigrbl
table/profile declares. Do not collapse protocol-specific equivalences into
ordinary REST CRUD route inventory.

The runtime proof must exercise the actual protocol named by the equivalence:

- REST equivalences may assert HTTP paths, methods, status codes, and JSON
  response bodies with `httpx`.
- HTTP JSON-RPC equivalences must send JSON-RPC 2.0 request envelopes over HTTP
  and assert JSON-RPC 2.0 response envelopes, including `jsonrpc`, `id`,
  `result` or `error`, and method identity.
- WebSocket equivalences must perform a real WebSocket handshake and exchange
  messages over a WebSocket client. OpenAPI route inventory is not evidence for
  WebSocket behavior.
- WebSocket JSON-RPC equivalences must additionally assert JSON-RPC framing,
  method identity, and subprotocol or contract gating when applicable.
- SSE, stream, and WebTransport equivalences must prove their stream or lane
  semantics directly, including ordering, completion, framing, and direction
  where those fields are part of the Tigrbl surface.

Framework limitations must be explicit in the equivalence row:

- FastAPI can express WebSocket analogues directly with `@app.websocket(...)`.
- Flask core plus Werkzeug WSGI cannot express native WebSocket behavior. A
  Flask-labelled WebSocket analogue must either use a declared extension/runtime
  such as Flask-Sock with a compatible server, use a Flask-adjacent ASGI
  framework such as Quart and label that explicitly, or be marked unsupported /
  not native. Do not claim native Flask parity through HTTP routes.
- FastAPI and Flask do not have first-class `http.jsonrpc` table primitives.
  Their analogues should be explicit HTTP `POST` JSON-RPC dispatch endpoints,
  not REST CRUD endpoints.

If the vendor implementation cannot run through the protocol-specific shared
client proof, the equivalence is not certifiable.

## Current Reference Shape

Use the Widget REST CRUD equivalence as the reference style:

- `equivalences/rest_table/tigrbl_impl.py` defines a `Widget`
  `RestTable` and module-level `app`.
- `equivalences/rest_table/fastapi_impl.py` defines the SQLAlchemy row,
  Pydantic models, FastAPI routes, and module-level `app`.
- `equivalences/rest_table/flask_impl.py` defines the SQLAlchemy row,
  Flask routes, and module-level `app`.
- `equivalences/rest_table/runtime.py` owns the equivalence-specific
  `httpx` client assertion sequence.
- `equivalences/rest_table/contract.py` maps each framework app to its
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
- Match the declared Tigrbl protocol/profile before matching superficial route
  shape.
- Keep Tigrbl examples pro-Tigrbl and direct: use Tigrbl table/app primitives.
- Keep FastAPI examples recognizably FastAPI: decorators, Pydantic models,
  SQLAlchemy where persistence is needed, and `@app.websocket` where the
  equivalence is WebSocket.
- Keep Flask examples recognizably Flask: decorators, request/jsonify, SQLAlchemy
  where persistence is needed. For WebSocket examples, use and declare the
  extension/runtime required to make Flask participate in a real WebSocket
  proof.
- Use SQLite for local persistence demonstrations unless the equivalence is
  explicitly about another engine.
- Keep shared mechanics in runtime modules: port selection, server startup,
  readiness polling, shutdown, client calls, and repeated expected evidence.
- Use asserts, not prints, to demonstrate expected behavior.
- Prefer module-level docstrings, class docstrings, method/function docstrings,
  and selective inline comments to explain the lesson.

Do not:

- Use REST endpoints as substitutes for JSON-RPC, WebSocket, SSE, stream, or
  WebTransport equivalences.
- Use OpenAPI path/method assertions as the only proof for non-REST protocols.
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
      rest_table/
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
    rest_table/
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

- Use stable IDs such as `table-class.rest-table`.
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
- protocol-appropriate server selection, including rejecting WSGI when the
  equivalence requires WebSocket behavior and no compatible extension/runtime is
  declared;
- port allocation;
- readiness polling;
- shutdown;
- shared client calls through the correct protocol client, such as `httpx` for
  HTTP and `websockets` for WebSocket;
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

Scope discipline is not permission to make a narrow cosmetic edit when the
equivalence is structurally wrong. If the requested change touches an
equivalence's behavioral claim, protocol, or vendor parity, inspect and update
the complete equivalence unit:

- `contract.py` claim, status, implementation metadata, and server kind;
- `runtime.py` protocol-specific client proof and expected evidence;
- `tigrbl_impl.py`, `fastapi_impl.py`, and `flask_impl.py`;
- pytest assertions that pin the expected evidence and prevent regression.

Do not stop after replacing fake vendor response payloads if the runtime still
certifies only OpenAPI route inventory for a non-REST protocol. That is an
incomplete and misleading equivalence. The minimum acceptable fix is to either
make the contract, runtime, implementations, and tests protocol-correct
together, or explicitly mark the framework/equivalence as unsupported,
not-native, or projection-only with evidence that matches that limitation.

Before committing an equivalence change, run a local audit against the edited
equivalence:

- Does the proof exercise the same protocol named by the Tigrbl table/profile?
- Does every vendor implementation expose that protocol through normal
  first-class framework authoring?
- Does the shared client assert payloads, frames, envelopes, ordering, lane
  direction, and completion semantics when those are part of the equivalence?
- Would a developer reading only the implementation file see a realistic
  framework example rather than scaffolding built to satisfy a route inventory?
- Would the test fail if the implementation fell back to ordinary REST or
  OpenAPI-only evidence?

When adding a new equivalence, update the matrix, implementation files, runtime
proof, and tests together in the same change. The result should be readable to a
human and certifiable by pytest.
