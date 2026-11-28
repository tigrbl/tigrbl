# tigrbl_engine_s3

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_engine_s3</strong></p>
<p align="center">Direct S3 API-backed object storage engine plugin for Tigrbl with optional content-addressed storage.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_s3/"><img alt="pypi: tigrbl_engine_s3" src="https://img.shields.io/pypi/v/tigrbl_engine_s3?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/pyproject.toml"><img alt="Layer: 090_engines" src="https://img.shields.io/static/v1?label=Layer&amp;message=090_engines&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_s3/"><img alt="Monthly PyPI downloads: tigrbl_engine_s3" src="https://img.shields.io/pypi/dm/tigrbl_engine_s3?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/README.md"><img alt="README hits: tigrbl_engine_s3" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/090_engines/tigrbl_engine_s3/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_engine_s3`: Direct S3 API-backed object storage engine plugin for Tigrbl with optional content-addressed storage.

### Why This Package

Use it when an application needs direct S3 request semantics, credential-chain
behavior, endpoint configuration, or server-side upload options.

### When to Use

Choose this package for direct boto3-compatible S3 calls. Choose
`tigrbl_engine_s3fs` when the fsspec/s3fs filesystem interface is preferable.

### Features

- `S3Engine`: declared in src/tigrbl_engine_s3/engine.py
- `S3Session`: declared in src/tigrbl_engine_s3/session.py

### Non-Goals

`tigrbl_engine_s3` owns direct S3 API-backed object storage engine plugin for Tigrbl with optional content-addressed storage. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/pyproject.toml) declares runtime dependencies including `boto3`, `tigrbl`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_engine_s3
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_engine_s3
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_engine_s3
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("tigrbl_engine_s3")
assert package.__name__ == "tigrbl_engine_s3"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `tigrbl_engine_s3`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("tigrbl_engine_s3")
assert package.__name__ == "tigrbl_engine_s3"
```
<!-- readme-standards:end example.usage -->

### Configuration

```python
from tigrbl import EngineSpec

engine, make_session = EngineSpec.from_any(
    {
        "kind": "s3",
        "bucket": "documents",
        "prefix": "tenant-a",
        "region_name": "us-east-1",
        "endpoint_url": "http://localhost:9000",
        "cas": True,
        "put_options": {"ServerSideEncryption": "AES256"},
    }
).build()
```

Credentials follow boto3's normal provider chain. Explicit `access_key`,
`secret_key`, and `session_token` mappings are also accepted. Tests and custom
integrations can inject an existing client as `mapping["client"]`.

### Error Handling

The inspected `tigrbl_engine_s3` source raises `FileNotFoundError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_engine_s3` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `S3Engine`, `S3Session`, `register`, `s3_capabilities`, `s3_engine`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

This package owns direct S3 object I/O, logical key normalization, local session
staging, upload options, and optional SHA-256 content-addressed storage. Its
engine implements the canonical `EngineBase` contract while retaining this
object-specific surface.

This README is the package-local distribution entry point for
`tigrbl_engine_s3`. Cross-package claims and release status remain governed by
the repository docs and `.ssot/registry.json`.

### Public API and Import Surfaces

- `S3Engine`
- `S3Session`
- `s3_engine()` and `s3_capabilities()`
- `register()` under the `tigrbl.engine` entry-point group

### Entry Points

<!-- readme-standards:begin entry-points -->
- `tigrbl.engine_plugins` → `s3` → `tigrbl_engine_s3:register`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_engine_s3` are `boto3`, `tigrbl`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/src/tigrbl_engine_s3/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_engine_s3` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_engine_s3`, use the source-declared public interfaces (`S3Engine`, `S3Session`, `register`, `s3_capabilities`, `s3_engine`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_engine_s3` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_engine_s3`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/src/tigrbl_engine_s3/__init__.py). The `tigrbl_engine_s3` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_engine_s3` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_engine_s3` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_s3_engine.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/tests/test_s3_engine.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

The implementation has package-scoped fake-backend tests and build validation.
It does not claim live AWS or S3-compatible service conformance yet.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/src/tigrbl_engine_s3/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_engine_s3` provides direct S3 API-backed object storage engine plugin for Tigrbl with optional content-addressed storage; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_engine_s3`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/src/tigrbl_engine_s3/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_engine_s3` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)

### Related Packages

- `tigrbl`
- `tigrbl_engine_s3fs`

### Project Links

<!-- readme-standards:begin project-links -->
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/090_engines/tigrbl_engine_s3)
- [pypi: tigrbl_engine_s3](https://pypi.org/project/tigrbl_engine_s3/)
<!-- readme-standards:end project-links -->

- [Discord](https://discord.gg/K4YTAPapjR)
- [GitHub Issues](https://github.com/tigrbl/tigrbl/issues)

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_engine_s3`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/090_engines/tigrbl_engine_s3` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_engine_s3?**

`tigrbl_engine_s3` is a standalone Tigrbl object-storage engine that calls the
S3 API directly through a boto3-compatible client. It supports AWS S3 and S3-
compatible services such as MinIO or R2 when configured with an endpoint URL.

**When should I install tigrbl_engine_s3?**

Install it for object-native Tigrbl workloads that should communicate through a
boto3-compatible S3 client.

**Who is tigrbl_engine_s3 for?**

It is for application developers and platform engineers integrating Tigrbl with
AWS S3 or an S3-compatible service.

**Where does tigrbl_engine_s3 fit?**

It is a layer-90 standalone engine package and depends on the public `tigrbl`
facade plus `boto3`.

**How does tigrbl_engine_s3 work?**

Its plugin builds an `S3Engine` and `S3Session`; sessions translate strict
logical object keys into direct `put_object`, `get_object`, and related calls.

**Install**

```bash
uv add tigrbl_engine_s3
```

**Surface Coverage**

The session API is object-native:

- `put_object(key, data)`, `get_object(key)`, `delete_object(key)`
- `object_exists(key)`, `head_object(key)`, `list_objects(prefix="")`
- optional `put_cas(data)`, `get_cas(address)`, `cas_exists(address)`

**Content-addressed storage**

CAS is opt-in with `"cas": True`. The returned address is `sha256:<hex>` and
the physical object is sharded below `.cas/sha256` by default. Retrieval hashes
the received bytes and fails if they do not match the requested address.

S3 is not a multi-object transactional store. `begin()` provides local staging
and rollback before upload, but `commit()` is a sequence of remote S3 calls and
can be partially applied if a later request fails.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_engine_s3` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_engine_s3` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/090_engines/tigrbl_engine_s3/NOTICE) for attribution.
<!-- readme-standards:end notices -->
