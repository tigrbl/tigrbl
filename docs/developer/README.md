# Developer Documentation

This section collects developer-facing summaries and pointers.

## Contents

- `AUTHORING_BCP.md` - convenient authoring path and best current practice, with grouped avoid/do/why and do-not/do/why guidance
- `EQUIVALENCE_INDEX.md` - reader path and vocabulary for authoring, transport, and engine equivalence guides
- `AUTHORING_EQUIVALENCE.md` - Tigrbl, Starlette, and FastAPI application authoring concept map
- `ROUTER_TABLE_EQUIVALENCE.md` - Tigrbl, FastAPI, and Flask router/table equivalence matrices
- `TRANSPORT_EQUIVALENCE.md` - ASGI 3, HTTP, streaming, SSE, WebSocket, WebTransport, and delegated carrier equivalence guide
- `ENGINE_SQL_EQUIVALENCE.md` - engine, SQLAlchemy, SQL dialect, datatype lowering, and backend plugin equivalence guide
- Generated equivalence blocks are maintained with `tools/docs/update_equivalence_docs.py --write` and checked by `tools/ci/validate_equivalence_docs.py`
- Certifiable equivalence runtime demos live in `examples/equivalence_contracts` and are checked by `tools/ci/validate_equivalence_runtime_contracts.py`
- `TRANSPORTS_AND_FRAMING.md` - current transport surface, binding, stream, carrier, framing, and fail-closed reference
- `API_REFERENCE.md` - high-level workspace and public surface inventory
- `OPERATOR_SURFACES.md` - current operator surface status summary
- `operator/README.md` - operator reference pages and current boundary decisions
- `CLI_REFERENCE.md` - implemented unified CLI surface, commands, flags, and smoke semantics
- `TESTING_GUIDE.md` - current certification lane model, test classes, and validation guidance
- `PACKAGE_CATALOG.md` - canonical workspace inventory for packages
- `PACKAGE_LAYERS.md` - dependency-oriented package layer index
- `PACKAGE_LAYOUT.md` - normalized package layout rules enforced by CI
- `CI_VALIDATION.md` - repository validation workflow and script inventory

## Existing specialized developer docs already in tree

- `docs/architecture/`
- `docs/migration/`
- `docs/testing/`
