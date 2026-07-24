# Experimental Tigrbl MCP

This experimental package projects Tigrbl operations onto MCP `2025-11-25`
using the official Python SDK's low-level APIs. It does not use the SDK's
high-level convenience server.

The implementation uses:

- `mcp.server.lowlevel.Server` for protocol dispatch and capability negotiation;
- `mcp.server.stdio.stdio_server` for stdio framing;
- `mcp.server.streamable_http_manager.StreamableHTTPSessionManager` for
  Streamable HTTP;
- explicit SDK handlers for tools, resources, resource templates, and prompts;
- `TigrblApp.rpc_call()` as the only execution path for projected operations.

## Explicit MCP handlers

`TigrblMCP.derive()` registers the two operation-backed handlers:

- `list_tools`
- `call_tool`

The note surface provider registers:

- `list_resources`
- `list_resource_templates`
- `read_resource`
- `list_prompts`
- `get_prompt`

Registering these handlers directly causes the low-level SDK to advertise the
corresponding MCP server capabilities during initialization.

## Factory vocabulary

```python
NOTE_MCP = TigrblMCP.define(...)
service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))
derived = TigrblMCP.derive(NOTE_MCP, existing_app)
server = service.provide()
```

The verbs have deliberately distinct contracts:

- `define(...) -> TigrblMCPDefinition` validates and freezes declarative input.
- `make(...) -> TigrblMCP` constructs and initializes a derived `TigrblApp`, then
  delegates to `derive`.
- `derive(definition, app) -> TigrblMCP` projects an existing initialized app
  onto a low-level MCP `Server`.
- `service.provide() -> Server` exposes that already-derived SDK server.

`provide` is therefore not a factory alias like `define`, `make`, or `derive`.
It is an instance-level provisioning/accessor boundary. It performs no creation,
initialization, registration, or derivation.

## ASGI scope by transport

Stdio transports MCP JSON-RPC over process streams, so it has no ASGI scope:

```python
assert service.asgi_app("stdio") is None
```

Streamable HTTP exposes an ASGI application at `/mcp`. A request receives a
normal ASGI HTTP scope such as:

```python
{
    "type": "http",
    "http_version": "1.1",
    "method": "POST",
    "scheme": "http",
    "path": "/mcp",
    "raw_path": b"/mcp",
    "query_string": b"",
    "root_path": "",
    "headers": [...],
    "client": ("127.0.0.1", 12345),
    "server": ("127.0.0.1", 8000),
}
```

## Run

```bash
uv run python server.py --transport stdio
uv run python server.py --transport streamable-http
```

The Streamable HTTP endpoint defaults to `http://127.0.0.1:8000/mcp`.

## Inspect

```powershell
& 'C:\Program Files\nodejs\npx.cmd' -y @modelcontextprotocol/inspector@0.21.2 `
  --cli .\.venv\Scripts\python.exe server.py --method tools/list
```

## Test

```bash
uv run --group dev pytest -q --basetemp .pytest-tmp
```