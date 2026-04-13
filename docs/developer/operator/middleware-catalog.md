# Built-in Middleware Catalog and Auth-Surface Decision

## Built-in middleware catalog

The current target now treats the middleware catalog as a bounded, closed surface consisting of:

- `Middleware` — the generic middleware protocol / wrapper surface
- `CORSMiddleware` — the built-in concrete middleware included in the framework package

This is intentionally a **bounded catalog**, not a promise of a large built-in middleware marketplace.

## Generic auth surface decision

The framework keeps auth **dependency/hook-based only** in the current cycle.

That means:

- security dependencies remain the first-class auth surface
- `AuthNProvider`, `set_auth(...)`, `allow_anon`, and authz callback hooks remain the governing abstractions
- the framework does **not** add a new monolithic generic auth middleware abstraction in this cycle

## Why

The dependency/hook-based model is already the working framework surface and is aligned with the existing OpenAPI/OpenRPC security machinery. Adding a second generic auth surface in this cycle would widen scope without being required to close the current operator boundary honestly.
