# tigrbl-transport-surface-matrix-demo

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-transport-surface-matrix-demo</strong></p>
<p align="center">Tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-transport-surface-matrix-demo/"><img alt="pypi: tigrbl-transport-surface-matrix-demo unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-transport-surface-matrix-demo%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml"><img alt="Layer: 96_examples" src="https://img.shields.io/static/v1?label=Layer&amp;message=96_examples&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-transport-surface-matrix-demo/"><img alt="pypi downloads: tigrbl-transport-surface-matrix-demo: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-transport-surface-matrix-demo%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/README.md"><img alt="README hits: tigrbl-transport-surface-matrix-demo" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/96_examples/transport_surface_matrix_demo/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

The [Transport Trace Lab](trace_lab/README.md) runs REST, HTTP JSON-RPC, WebSocket, and WebTransport with a live identity timeline.

### Summary

This UV project collects the transport-surface demos requested for the current checkout into one runnable app:

- `h1.1`, `h2`, `h3/quic`
- `h1.1/h2/h3` with REST
- `h1.1/h2/h3` with JSON-RPC
- `stream`
- `sse`
- `stream ndjson`
- `websocket (ws/wss)`
- `wss + ndjson`
- `wss + jsonrpc`
- `mtls`
- `webtransport (single session with 1 unidirectional stream, 1 bidirectional stream, and datagram messages)`

The app entrypoint is `pkgs/96_examples/transport_surface_matrix_demo/app.py`.

### Why This Package

Use this project for tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.

### When to Use

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

### Features

- Public source surface: the checkout commands documented in Quick Start.
- Declared responsibility: Tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-transport-surface-matrix-demo` owns tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml) declares runtime dependencies including `tigrbl`, `tigrbl-core`, `tigrbl-kernel`, `httpx`, `uvicorn`. Use the source-checkout workflow for this workspace or test harness.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
This is a source-only workspace or test harness, not an installable distribution. From its checkout, synchronize the declared environment:

```bash
uv sync
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
This is a source-only workspace or test harness, not an installable distribution. Use the uv checkout workflow above; this installer does not install the harness itself.
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
This is a source-only workspace or test harness, not an installable distribution. Use the uv checkout workflow above; this installer does not install the harness itself.
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/docs/readme/quick_start.sh).

```bash
uv run --directory pkgs/96_examples/transport_surface_matrix_demo python -c "import app"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-transport-surface-matrix-demo` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/docs/readme/usage.sh).

```bash
uv run --directory pkgs/96_examples/transport_surface_matrix_demo python -c "import app"
```
<!-- readme-standards:end example.usage -->

The walkthrough above is retained. The entry surface can be loaded with:

### Configuration

Configure `tigrbl-transport-surface-matrix-demo` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-transport-surface-matrix-demo` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml).

### Best Practices

Use the explicit `tigrbl-transport-surface-matrix-demo` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

Tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.

### Public API and Import Surfaces

The transport demonstration app in app.py. See the project source and existing examples above for supported call signatures.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-transport-surface-matrix-demo` are `tigrbl`, `tigrbl-core`, `tigrbl-kernel`, `httpx`, `uvicorn`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl-transport-surface-matrix-demo` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl-transport-surface-matrix-demo`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-transport-surface-matrix-demo` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-transport-surface-matrix-demo`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml). The `tigrbl-transport-surface-matrix-demo` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-transport-surface-matrix-demo` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-transport-surface-matrix-demo` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_transport_surface_matrix_demo.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/tests/test_transport_surface_matrix_demo.py)
- [tests/test_transport_surface_matrix_demo_tigrcorn_e2e_matrix.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/tests/test_transport_surface_matrix_demo_tigrcorn_e2e_matrix.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-transport-surface-matrix-demo` provides tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-transport-surface-matrix-demo`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-transport-surface-matrix-demo` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/transport_surface_matrix_demo)

### Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: tigrbl-transport-surface-matrix-demo](https://pypi.org/project/tigrbl-transport-surface-matrix-demo/)
<!-- readme-standards:end project-links -->

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-transport-surface-matrix-demo`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/96_examples/transport_surface_matrix_demo` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What Is Runnable Now**

| Demo | Path / surface | Repo-grounded status |
|---|---|---|
| REST | `/items`, `/items/{id}` | runnable |
| JSON-RPC | `/rpc` | runnable |
| stream | `/stream/raw` | runnable |
| stream ndjson | `/stream/ndjson` | runnable |
| sse | `/sse/events` | runnable |
| websocket `ws` | `/ws/echo` | runnable |
| websocket `wss` | `/wss/echo` | runnable at app/binding level; needs TLS-capable serving layer |
| `wss + jsonrpc` | `/wss/jsonrpc` | runnable at app/binding level; requires `jsonrpc` subprotocol |
| `wss + ndjson` | fail-closed negative demo | rejected without the required `ndjson` subprotocol |
| mtls | `/mtls/echo` | docs and security-scheme demo are runnable; real client cert exchange depends on serving layer and cert material |
| webtransport session | `/transport/session` | provisional binding demo; the app models the session payload and metadata honestly, but this repo does not yet claim a mature release-grade WebTransport server path |

**Serve The Demo**

Run the bundle with the CLI:

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server uvicorn --host 127.0.0.1 --port 8000
```

Available docs surfaces:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/openrpc.json`
- `http://127.0.0.1:8000/zdoc`
- `http://127.0.0.1:8000/asyncapi.json`
- `http://127.0.0.1:8000/matrix`

**HTTP Profile Demos**

These rows are operator-control demos. The same app is served with different blessed profile settings; actual protocol negotiation depends on the selected server.

**h1.1**

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server uvicorn --deployment-profile strict-h1-origin --proxy-contract strict --early-data-policy reject
```

**h2**

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server hypercorn --deployment-profile strict-h2-origin --proxy-contract strict --early-data-policy reject --http2-max-concurrent-streams 128 --http2-initial-window-size 65535
```

**h3 / quic**

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server tigrcorn --deployment-profile strict-h3-edge --proxy-contract edge-normalized --early-data-policy edge-replay-guarded --quic-metrics connections,handshake,retry,migration
```

**Test**

```powershell
cd .\examples\transport_surface_matrix_demo
uv run pytest
```

**REST And JSON-RPC Over H1/H2/H3**

REST demo calls:

```powershell
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\":\"Ada\"}"
curl http://127.0.0.1:8000/items/1
```

JSON-RPC demo calls:

```powershell
curl -X POST http://127.0.0.1:8000/rpc -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"DemoItem.create\",\"params\":{\"name\":\"Ada\"},\"id\":1}"
curl -X POST http://127.0.0.1:8000/rpc -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"DemoItem.read\",\"params\":{\"id\":1},\"id\":2}"
```

**Websocket Notes**

- `ws/wss` text echo uses `/ws/echo` and `/wss/echo`.
- `wss + jsonrpc` uses `/wss/jsonrpc` and requires the `jsonrpc` subprotocol.
- `wss + ndjson` requires the `ndjson` subprotocol. The negative demo intentionally omits that subprotocol so `WsBindingSpec(proto="wss", framing="ndjson")` still raises before runtime dispatch.

**mTLS Notes**

For the app-side security scheme and route:

- serve the app with `--deployment-profile strict-mtls-origin --ocsp-policy strict --revocation-policy strict`
- hit `/mtls/echo`

For client-side transport guidance, see the [authoring guide](../../../docs/developer/AUTHORING_BCP.md).

**WebTransport Notes**

`/transport/session` returns one honest session payload with:

- one unidirectional stream row
- one bidirectional stream row
- one client-to-server datagram and one server-to-client datagram

That matches the requested demo shape while staying honest that current repo support is still provisional at the WebTransport transport boundary.

**What is tigrbl-transport-surface-matrix-demo?**

Tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.

**When should I install tigrbl-transport-surface-matrix-demo?**

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

**Who is tigrbl-transport-surface-matrix-demo for?**

Tigrbl maintainers and application developers working with this project’s APIs.

**Where does tigrbl-transport-surface-matrix-demo fit?**

Source: `pkgs/96_examples/transport_surface_matrix_demo` in the Tigrbl workspace.

**How does tigrbl-transport-surface-matrix-demo work?**

The transport demonstration app in app.py. The examples and implementation above describe the configuration and execution flow.

**Install**

From the repository root:

```console
uv sync --project pkgs/96_examples/transport_surface_matrix_demo
```

**Surface Coverage**

| Surface | Value |
| --- | --- |
| Project | `tigrbl-transport-surface-matrix-demo` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `app.py` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-transport-surface-matrix-demo` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-transport-surface-matrix-demo` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/LICENSE).
<!-- readme-standards:end license -->

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/transport_surface_matrix_demo/NOTICE) for attribution.
<!-- readme-standards:end notices -->
