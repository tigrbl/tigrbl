# Docs and Spec Endpoints

## Kept and implemented in the current target

The framework keeps these public docs/spec surfaces:

- `/openapi.json`
- Swagger UI at `/docs`
- `/openrpc.json`
- Lens / OpenRPC UI at `/lens`
- JSON Schema bundle at `/schemas.json`

## Unsupported / de-scoped UI rows

The current cycle does **not** retain these interactive UI rows:

- AsyncAPI spec generation, mounting, and UI - unsupported
- JSON Schema UI - de-scoped to a later target while `/schemas.json` stays in scope
- OIDC discovery/docs surface - de-scoped from the current cycle

## Rationale

The framework already owns the underlying spec emission surfaces. The missing interactive UIs and OIDC discovery/docs routes were not honestly closed, so the current target keeps the emitted specs and de-scopes the unimplemented UI/discovery surfaces instead of overstating closure.
