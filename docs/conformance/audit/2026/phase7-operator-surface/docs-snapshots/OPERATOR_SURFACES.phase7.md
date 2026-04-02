# Operator Surfaces

## Closed now

- REST
- JSON-RPC surface
- request/response surface
- templating
- middleware protocol
- bounded built-in middleware catalog (`Middleware`, `CORSMiddleware`)
- OpenAPI JSON
- Swagger UI
- OpenRPC JSON
- Lens / OpenRPC UI
- JSON Schema bundle at `/schemas.json`
- AsyncAPI spec at `/asyncapi.json`
- OAS security scheme modeling for `apiKey`, `http`, `oauth2`, `openIdConnect`, and `mutualTLS`
- auth/security plumbing through `AuthNProvider`, route/app auth configuration, security dependencies, and authz hooks
- static files
- cookies
- streaming responses
- WebSockets
- WHATWG SSE
- forms / multipart
- upload handling

## De-scoped UI / discovery rows

- AsyncAPI UI
- JSON Schema UI
- OIDC discovery/docs surface

## Current auth-model decision

The generic auth surface remains dependency/hook-based only.
