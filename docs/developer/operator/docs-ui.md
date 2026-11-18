# Docs and Spec Endpoints

## Kept and implemented in the current target

The framework keeps these public docs/spec surfaces:

- `/openapi.json`
- Swagger UI at `/docs`
- `/openrpc.json`
- ZDoc at `/zdoc` shows REST and JSON-RPC in one viewer. Compatibility bookmarks at `/lens` also serve ZDoc.
- An app can add a WebSocket tab with `app.mount_zdoc(asyncapi_path="/websocket-spec.json")` and serve its own AsyncAPI 3.0 JSON document at that path.
- JSON Schema bundle at `/schemas.json`

## Unsupported / de-scoped UI rows

The current cycle does **not** retain these interactive UI rows:

- Framework generation and default mounting of an AsyncAPI payload are unsupported. ZDoc accepts a document served by the application.
- JSON Schema UI - de-scoped to a later target while `/schemas.json` stays in scope
- OIDC discovery/docs surface - de-scoped from the current cycle

## Rationale

The framework already owns the underlying spec emission surfaces. The missing interactive UIs and OIDC discovery/docs routes were not honestly closed, so the current target keeps the emitted specs and de-scopes the unimplemented UI/discovery surfaces instead of overstating closure.
