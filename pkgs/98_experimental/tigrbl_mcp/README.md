# tigrbl-mcp

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-mcp</strong></p>
<p align="center">Experimental low-level MCP SDK integration for Tigrbl operations.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-mcp/"><img alt="pypi: tigrbl-mcp unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-mcp%20unpublished&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml"><img alt="Layer: 98_experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=98_experimental&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-mcp/"><img alt="pypi downloads: tigrbl-mcp: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-mcp%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/README.md"><img alt="README hits: tigrbl-mcp" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/98_experimental/tigrbl_mcp/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

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

### Why This Package

Use this project for experimental low-level MCP SDK integration for Tigrbl operations.

### When to Use

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

### Features

- Public source surface: the checkout commands documented in Quick Start.
- Declared responsibility: Experimental low-level MCP SDK integration for Tigrbl operations.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-mcp` owns experimental low-level MCP SDK integration for Tigrbl operations. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml) declares runtime dependencies including `mcp`, `tigrbl`, `tigrbl-core`, `uvicorn`. Use the source-checkout workflow for this workspace or test harness.

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
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/docs/readme/quick_start.py).

```python
import tigrbl_mcp
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-mcp` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/docs/readme/usage.py).

```python
import tigrbl_mcp
```
<!-- readme-standards:end example.usage -->

The walkthrough above is retained. The entry surface can be loaded with:

### Configuration

Configure `tigrbl-mcp` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-mcp` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml).

### Best Practices

Use the explicit `tigrbl-mcp` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

Experimental low-level MCP SDK integration for Tigrbl operations.

### Public API and Import Surfaces

TigrblMCP operation projection and SDK server integration. See the project source and existing examples above for supported call signatures.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-mcp` are `mcp`, `tigrbl`, `tigrbl-core`, `uvicorn`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl-mcp` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl-mcp`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-mcp` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-mcp`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml). The `tigrbl-mcp` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-mcp` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-mcp` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_tigrbl_mcp_server.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/tests/test_tigrbl_mcp_server.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-mcp` provides experimental low-level MCP SDK integration for Tigrbl operations; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-mcp`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-mcp` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/98_experimental/tigrbl_mcp)

### Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: tigrbl-mcp](https://pypi.org/project/tigrbl-mcp/)
<!-- readme-standards:end project-links -->

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-mcp`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/98_experimental/tigrbl_mcp` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Explicit MCP handlers**

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

**Factory vocabulary**

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

**ASGI scope by transport**

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

**Run**

```bash
uv run python server.py --transport stdio
uv run python server.py --transport streamable-http
```

The Streamable HTTP endpoint defaults to `http://127.0.0.1:8000/mcp`.

**Inspect**

```powershell
& 'C:\Program Files\nodejs\npx.cmd' -y @modelcontextprotocol/inspector@0.21.2 `
  --cli .\.venv\Scripts\python.exe server.py --method tools/list
```

**Test**

```bash
uv run --group dev pytest -q --basetemp .pytest-tmp
```

**What is tigrbl-mcp?**

Experimental low-level MCP SDK integration for Tigrbl operations.

**When should I install tigrbl-mcp?**

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

**Who is tigrbl-mcp for?**

Tigrbl maintainers and application developers working with this project’s APIs.

**Where does tigrbl-mcp fit?**

Source: `pkgs/98_experimental/tigrbl_mcp` in the Tigrbl workspace.

**How does tigrbl-mcp work?**

TigrblMCP operation projection and SDK server integration. The examples and implementation above describe the configuration and execution flow.

**Install**

From the repository root:

```console
uv sync --project pkgs/98_experimental/tigrbl_mcp
```

**Surface Coverage**

| Surface | Value |
| --- | --- |
| Project | `tigrbl-mcp` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_mcp.py` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-mcp` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-mcp` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/LICENSE).
<!-- readme-standards:end license -->

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/98_experimental/tigrbl_mcp/NOTICE) for attribution.
<!-- readme-standards:end notices -->
