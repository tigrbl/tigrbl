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

## What is tigrbl-mcp?

Experimental low-level MCP SDK integration for Tigrbl operations.

## Why use tigrbl-mcp?

Use this project for experimental low-level MCP SDK integration for Tigrbl operations.

## When should I install tigrbl-mcp?

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

## Who is tigrbl-mcp for?

Tigrbl maintainers and application developers working with this project’s APIs.

## Where does tigrbl-mcp fit?

Source: `pkgs/98_experimental/tigrbl_mcp` in the Tigrbl workspace.

## How does tigrbl-mcp work?

TigrblMCP operation projection and SDK server integration. The examples and implementation above describe the configuration and execution flow.

## Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

## Install

From the repository root:

```console
uv sync --project pkgs/98_experimental/tigrbl_mcp
```

## Surface Coverage

| Surface | Value |
| --- | --- |
| Project | `tigrbl-mcp` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_mcp.py` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

## What It Owns

Experimental low-level MCP SDK integration for Tigrbl operations.

## Public API and Import Surface

TigrblMCP operation projection and SDK server integration. See the project source and existing examples above for supported call signatures.

## Usage Examples

The walkthrough above is retained. The entry surface can be loaded with:

```python
import tigrbl_mcp
```

## How To Choose This Package

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

## Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

## Documentation Links

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/98_experimental/tigrbl_mcp)

## Support

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

## License

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)
