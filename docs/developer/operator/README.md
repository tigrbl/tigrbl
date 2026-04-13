# Operator Surface Reference

This section documents the current-target framework/operator surfaces that remain in scope after the Phase 7 closure decisions.

## Surfaces documented here

- Docs and spec endpoints: `docs-ui.md`
- Static files: `static-files.md`
- Cookies and streaming responses: `cookies-and-streaming.md`
- WebSockets and SSE: `websockets-and-sse.md`
- Forms and uploads: `forms-and-uploads.md`
- Built-in middleware catalog and auth-surface decision: `middleware-catalog.md`
- Tigrcorn deployment profiles: `profiles/`

## Boundary decisions recorded here

- keep `/openapi.json`, Swagger UI, `/openrpc.json`, and Lens / OpenRPC UI
- keep AsyncAPI spec emission at `/asyncapi.json`, but de-scope interactive AsyncAPI UI to a later target
- keep JSON Schema bundle emission at `/schemas.json`, but de-scope interactive JSON Schema UI to a later target
- de-scope the OIDC discovery/docs surface from the current cycle
- keep the generic auth surface dependency/hook-based only rather than adding a new monolithic auth middleware abstraction in this cycle
- keep Tigrcorn hardening/profile certification fail-closed until external-runtime evidence lanes pass
