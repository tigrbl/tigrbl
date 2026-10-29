# Tigrbl WebSocket Realtime JSON-RPC Framework Demo

This UV project demonstrates the canonical framework declaration shape for
WebSocket realtime JSON-RPC ops:

- `AppSpec`
- `RouterSpec`
- `PathSpec(kind="ws-jsonrpc")`
- `TableSpec`
- `OpSpec`

The ops share one WebSocket connect path, use `JsonRpcFramingSpec`, infer the
`jsonrpc` subprotocol from framing, and lower through `TigrblApp.from_spec(...)`
into a route whose WebSocket JSON-RPC session behavior is composed by the
kernel from transport, framing, dispatch, and emit atoms.

It does not implement an app-local receive loop, JSON parser, op switch, send
loop, broadcast loop, or cleanup block. Those are kernel/atom/runtime
responsibilities governed by `adr:1199` and `spc:1147`.

## Test

```powershell
cd .\examples\websocket_realtime_ops
uv run pytest
```

## Declared Ops

```text
/ws/realtime
  Thread
    subscribe -> target=subscribe
    publish   -> target=publish
  Message
    create    -> target=create
```

`Thread.subscribe` is a finite JSON-RPC request/response op that registers
session-scoped interest with the framework realtime broker and acknowledges the
subscription. `Thread.publish` is an explicit fanout op that emits a JSON-RPC
notification to matching subscribers. `Message.create` is present to show that
OLTP create does not publish unless a publish effect is declared.


## What is tigrbl-websocket-realtime-ops-demo?

Tigrbl WebSocket realtime JSON-RPC framework declaration example.

## Why use tigrbl-websocket-realtime-ops-demo?

Use this project for tigrbl WebSocket realtime JSON-RPC framework declaration example.

## When should I install tigrbl-websocket-realtime-ops-demo?

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

## Who is tigrbl-websocket-realtime-ops-demo for?

Tigrbl maintainers and application developers working with this project’s APIs.

## Where does tigrbl-websocket-realtime-ops-demo fit?

Source: `pkgs/96_examples/websocket_realtime_ops` in the Tigrbl workspace.

## How does tigrbl-websocket-realtime-ops-demo work?

Declarative realtime JSON-RPC app and its operation specifications. The examples and implementation above describe the configuration and execution flow.

## Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

## Install

From the repository root:

```console
uv sync --project pkgs/96_examples/websocket_realtime_ops
```

## Surface Coverage

| Surface | Value |
| --- | --- |
| Project | `tigrbl-websocket-realtime-ops-demo` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `app.py` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

## What It Owns

Tigrbl WebSocket realtime JSON-RPC framework declaration example.

## Public API and Import Surface

Declarative realtime JSON-RPC app and its operation specifications. See the project source and existing examples above for supported call signatures.

## Usage Examples

The walkthrough above is retained. The entry surface can be loaded with:

```console
uv run --directory pkgs/96_examples/websocket_realtime_ops python -c "import app"
```

## How To Choose This Package

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

## Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

## Documentation Links

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/websocket_realtime_ops)

## Support

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

## License

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)
