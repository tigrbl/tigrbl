# tigrbl-websocket-realtime-ops-demo

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-websocket-realtime-ops-demo</strong></p>
<p align="center">Tigrbl WebSocket realtime JSON-RPC framework declaration example.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-websocket-realtime-ops-demo/"><img alt="pypi: tigrbl-websocket-realtime-ops-demo unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-websocket-realtime-ops-demo%20unpublished&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml"><img alt="Layer: 96_examples" src="https://img.shields.io/static/v1?label=Layer&amp;message=96_examples&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-websocket-realtime-ops-demo/"><img alt="pypi downloads: tigrbl-websocket-realtime-ops-demo: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-websocket-realtime-ops-demo%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/README.md"><img alt="README hits: tigrbl-websocket-realtime-ops-demo" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/96_examples/websocket_realtime_ops/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

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

### Why This Package

Use this project for tigrbl WebSocket realtime JSON-RPC framework declaration example.

### When to Use

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

### Features

- Public source surface: the checkout commands documented in Quick Start.
- Declared responsibility: Tigrbl WebSocket realtime JSON-RPC framework declaration example.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-websocket-realtime-ops-demo` owns tigrbl WebSocket realtime JSON-RPC framework declaration example. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml) declares runtime dependencies including `tigrbl`, `tigrbl-core`. Use the source-checkout workflow for this workspace or test harness.

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
Source: [docs/readme/quick_start.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/docs/readme/quick_start.sh).

```bash
uv run --directory pkgs/96_examples/websocket_realtime_ops python -c "import app"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-websocket-realtime-ops-demo` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/docs/readme/usage.sh).

```bash
uv run --directory pkgs/96_examples/websocket_realtime_ops python -c "import app"
```
<!-- readme-standards:end example.usage -->

The walkthrough above is retained. The entry surface can be loaded with:

### Configuration

Configure `tigrbl-websocket-realtime-ops-demo` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-websocket-realtime-ops-demo` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml).

### Best Practices

Use the explicit `tigrbl-websocket-realtime-ops-demo` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

Tigrbl WebSocket realtime JSON-RPC framework declaration example.

### Public API and Import Surfaces

Declarative realtime JSON-RPC app and its operation specifications. See the project source and existing examples above for supported call signatures.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-websocket-realtime-ops-demo` are `tigrbl`, `tigrbl-core`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl-websocket-realtime-ops-demo` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl-websocket-realtime-ops-demo`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-websocket-realtime-ops-demo` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-websocket-realtime-ops-demo`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml). The `tigrbl-websocket-realtime-ops-demo` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-websocket-realtime-ops-demo` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-websocket-realtime-ops-demo` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_websocket_realtime_ops_demo.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/tests/test_websocket_realtime_ops_demo.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-websocket-realtime-ops-demo` provides tigrbl WebSocket realtime JSON-RPC framework declaration example; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-websocket-realtime-ops-demo`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-websocket-realtime-ops-demo` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/websocket_realtime_ops)

### Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: tigrbl-websocket-realtime-ops-demo](https://pypi.org/project/tigrbl-websocket-realtime-ops-demo/)
<!-- readme-standards:end project-links -->

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-websocket-realtime-ops-demo`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/96_examples/websocket_realtime_ops` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Test**

```powershell
cd .\examples\websocket_realtime_ops
uv run pytest
```

**Declared Ops**

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

**What is tigrbl-websocket-realtime-ops-demo?**

Tigrbl WebSocket realtime JSON-RPC framework declaration example.

**When should I install tigrbl-websocket-realtime-ops-demo?**

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

**Who is tigrbl-websocket-realtime-ops-demo for?**

Tigrbl maintainers and application developers working with this project’s APIs.

**Where does tigrbl-websocket-realtime-ops-demo fit?**

Source: `pkgs/96_examples/websocket_realtime_ops` in the Tigrbl workspace.

**How does tigrbl-websocket-realtime-ops-demo work?**

Declarative realtime JSON-RPC app and its operation specifications. The examples and implementation above describe the configuration and execution flow.

**Install**

From the repository root:

```console
uv sync --project pkgs/96_examples/websocket_realtime_ops
```

**Surface Coverage**

| Surface | Value |
| --- | --- |
| Project | `tigrbl-websocket-realtime-ops-demo` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `app.py` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-websocket-realtime-ops-demo` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-websocket-realtime-ops-demo` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/LICENSE).
<!-- readme-standards:end license -->

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/websocket_realtime_ops/NOTICE) for attribution.
<!-- readme-standards:end notices -->
