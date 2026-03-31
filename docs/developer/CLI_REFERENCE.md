# CLI Reference

## Current state

There is currently **no unified `tigrbl` CLI** implemented in this checkpoint.

## Target contract

The current-target program expects:

- `tigrbl run`
- `tigrbl serve`
- `tigrbl dev`
- `tigrbl routes`
- `tigrbl openapi`
- `tigrbl openrpc`
- `tigrbl doctor`
- `tigrbl capabilities`

### Target flags

- `--server {tigrcorn,uvicorn,hypercorn,gunicorn}`
- `--host`
- `--port`
- `--reload`
- `--workers`
- `--root-path`
- `--proxy-headers`
- `--uds`
- `--docs-path`
- `--openapi-path`
- `--openrpc-path`
- `--lens-path`

This document records the contract and the current absence of the implementation so the repo state is explicit rather than ambiguous.
