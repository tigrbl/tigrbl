# ZDoc mount verification

On 2026-11-17, 31 pytest checks passed against the Tigrbl source tree on Windows with Python 3.13.14. The run covered system UI routes, OpenRPC and JSON-RPC behavior, and Lens compatibility mounts over Uvicorn.

The system UI tests checked that the legacy builder emits a migration warning, that /lens and /zdoc return the same viewer, and that the REST, JSON-RPC, and optional AsyncAPI URLs are joined to the app and proxy prefixes. The Uvicorn tests exercised default and custom OpenRPC payload paths through the deprecated mount entry points.

A further 14 pytest checks passed across system UI mounts, document builders, spec snapshots, and canonical AppSpec lowering. A browser run against the transport demo with locally bundled assets observed REST HTTP 200, JSON-RPC HTTP 200 with result `[]`, and a WebSocket echo followed by a normal closure (1000).
