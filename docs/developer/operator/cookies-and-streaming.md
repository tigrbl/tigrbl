# Cookies and Streaming Responses

## Cookies

The framework now treats cookies as a closed operator surface for the current target:

- request cookie access through `Request.cookies`
- response cookie setting through `Response.set_cookie(...)`
- request/response round-trip behavior covered in the Phase 7 operator tests

## Streaming responses

The framework now exposes streaming as a closed operator surface:

- `StreamingResponse(...)` supports sync and async iterables
- the ASGI send path emits multiple body frames instead of eagerly collapsing the payload into a single body message

## Notes

The current target closes the operator surface itself. Broader performance tuning or transport-level server concerns remain outside the framework certification boundary.
