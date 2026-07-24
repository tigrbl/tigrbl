# Tigrbl MCP Server

This example exposes an in-process Tigrbl-backed note service through the stable MCP
`2025-11-25` protocol using the official Python SDK.

It demonstrates:

- a `TigrblMCP` factory surface built around `define`, `make`, `derive`, and
  `provide`, with no application-specific build helper;
- three model-callable tools whose execution routes through
  `TigrblApp.rpc_call()`;
- a `note://{note_id}` resource template;
- a `summarize_note` prompt;
- deterministic projection of bound Tigrbl `OpSpec` input/output schemas into
  an MCP tool catalog;
- explicit, opt-in MCP exposure policy in `OpSpec.extra["mcp"]`;
- both stdio and Streamable HTTP server entry points.

## Factory lifecycle

`app.py` defines the declarative service once:

```python
NOTE_MCP = TigrblMCP.define(
    name="tigrbl-notes",
    tables=(Note,),
    tools={
        "create_note": _create_note_tool,
        "read_note": _read_note_tool,
        "list_notes": _list_notes_tool,
    },
    surfaces=(_provide_note_surfaces,),
    instructions="Create and read notes.",
)
```

Create an initialized Tigrbl application and its MCP projection with `make`:

```python
service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))
```

Project an existing initialized `TigrblApp` with `derive`, and obtain the
configured official-SDK server with `provide`:

```python
derived = TigrblMCP.derive(NOTE_MCP, existing_app)
mcp = derived.provide()
```

## ASGI scope by transport

Stdio does not enter ASGI. It carries MCP JSON-RPC messages over stdin/stdout, so
there is no `scope`, `receive`, or `send`, and the factory reports this directly:

```python
assert service.asgi_app("stdio") is None
```

Streamable HTTP is an ASGI application. For an MCP request, the ASGI server
creates an ordinary HTTP scope shaped like this (connection-specific values are
illustrative):

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

The corresponding application is available with:

```python
mcp_asgi = service.asgi_app("streamable-http")
```

`server.py` still delegates process startup to the official SDK's `run` method;
`asgi_app` exists for inspection, testing, or mounting into another ASGI host.

## Run

From this directory:

```bash
uv run python server.py --transport stdio
uv run python server.py --transport streamable-http
```

The Streamable HTTP endpoint is `http://127.0.0.1:8000/mcp` by default.

## Inspect

For a headless stdio check from PowerShell:

```powershell
& 'C:\Program Files\nodejs\npx.cmd' -y @modelcontextprotocol/inspector@0.21.2 `
  --cli .\.venv\Scripts\python.exe server.py --method tools/list
```

For interactive inspection, start the HTTP server, run:

```bash
npx -y @modelcontextprotocol/inspector
```

and connect the Inspector to `http://127.0.0.1:8000/mcp`.

## Test

```bash
uv run --group dev pytest -q --basetemp .pytest-tmp
```