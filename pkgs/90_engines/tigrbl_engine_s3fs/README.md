# tigrbl_engine_s3fs

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_engine_s3fs</strong></p>
<p align="center">S3FS-backed object storage engine plugin for Tigrbl with optional content-addressed storage.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_s3fs/"><img alt="pypi: tigrbl_engine_s3fs" src="https://img.shields.io/pypi/v/tigrbl_engine_s3fs"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/pyproject.toml"><img alt="Layer: 90_engines" src="https://img.shields.io/static/v1?label=Layer&amp;message=90_engines&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_s3fs/"><img alt="Monthly PyPI downloads: tigrbl_engine_s3fs" src="https://img.shields.io/pypi/dm/tigrbl_engine_s3fs"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/README.md"><img alt="README hits: tigrbl_engine_s3fs" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/90_engines/tigrbl_engine_s3fs/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_engine_s3fs`: S3FS-backed object storage engine plugin for Tigrbl with optional content-addressed storage.

### Why This Package

Use it when an application already uses the fsspec/s3fs ecosystem or needs a
filesystem-shaped adapter over S3 object storage.

### When to Use

Choose this package for the s3fs/fsspec interface. Choose `tigrbl_engine_s3`
when direct access to the boto3 S3 API and its request options is preferable.

### Features

- `S3FSEngine`: declared in src/tigrbl_engine_s3fs/engine.py
- `S3FSSession`: declared in src/tigrbl_engine_s3fs/session.py

### Non-Goals

`tigrbl_engine_s3fs` owns s3FS-backed object storage engine plugin for Tigrbl with optional content-addressed storage. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/pyproject.toml) declares runtime dependencies including `s3fs`, `tigrbl`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_engine_s3fs
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_engine_s3fs
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_engine_s3fs
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("tigrbl_engine_s3fs")
assert package.__name__ == "tigrbl_engine_s3fs"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `tigrbl_engine_s3fs`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("tigrbl_engine_s3fs")
assert package.__name__ == "tigrbl_engine_s3fs"
```
<!-- readme-standards:end example.usage -->

### Configuration

```python
from tigrbl import EngineSpec

engine, make_session = EngineSpec.from_any(
    {
        "kind": "s3fs",
        "bucket": "documents",
        "prefix": "tenant-a",
        "endpoint_url": "http://localhost:9000",
        "key": "minioadmin",
        "secret": "minioadmin",
        "cas": True,
    }
).build()
```

For custom clients and tests, pass an existing filesystem as `mapping["fs"]`.
All keys are bucket-relative and reject absolute paths and traversal segments.

### Error Handling

The inspected `tigrbl_engine_s3fs` source raises `FileNotFoundError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_engine_s3fs` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `S3FSEngine`, `S3FSSession`, `register`, `s3fs_capabilities`, `s3fs_engine`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

This package owns s3fs-backed object I/O, logical key normalization, local
session staging, and optional SHA-256 content-addressed storage. Its engine
implements the canonical `EngineBase` contract while retaining this
object-specific surface.

This README is the package-local distribution entry point for
`tigrbl_engine_s3fs`. Cross-package claims and release status remain governed
by the repository docs and `.ssot/registry.json`.

### Public API and Import Surfaces

- `S3FSEngine`
- `S3FSSession`
- `s3fs_engine()` and `s3fs_capabilities()`
- `register()` under the `tigrbl.engine` entry-point group

### Entry Points

<!-- readme-standards:begin entry-points -->
- `tigrbl.engine_plugins` → `s3fs` → `tigrbl_engine_s3fs:register`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_engine_s3fs` are `s3fs`, `tigrbl`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/src/tigrbl_engine_s3fs/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_engine_s3fs` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_engine_s3fs`, use the source-declared public interfaces (`S3FSEngine`, `S3FSSession`, `register`, `s3fs_capabilities`, `s3fs_engine`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_engine_s3fs` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_engine_s3fs`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/src/tigrbl_engine_s3fs/__init__.py). The `tigrbl_engine_s3fs` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_engine_s3fs` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_engine_s3fs` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_s3fs_engine.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/tests/test_s3fs_engine.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

The implementation has package-scoped fake-backend tests and build validation.
It does not claim live AWS or S3-compatible service conformance yet.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/src/tigrbl_engine_s3fs/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_engine_s3fs` provides s3FS-backed object storage engine plugin for Tigrbl with optional content-addressed storage; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_engine_s3fs`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/src/tigrbl_engine_s3fs/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_engine_s3fs` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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
- `tigrbl_engine_s3`

### Project Links

<!-- readme-standards:begin project-links -->
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_s3fs)
- [pypi: tigrbl_engine_s3fs](https://pypi.org/project/tigrbl_engine_s3fs/)
<!-- readme-standards:end project-links -->

- [Discord](https://discord.gg/K4YTAPapjR)
- [GitHub Issues](https://github.com/tigrbl/tigrbl/issues)

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_engine_s3fs`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/90_engines/tigrbl_engine_s3fs` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_engine_s3fs?**

`tigrbl_engine_s3fs` is a standalone Tigrbl object-storage engine backed by
the synchronous `s3fs.S3FileSystem` interface. It supports AWS S3 and S3-
compatible endpoints accepted by `s3fs`.

**When should I install tigrbl_engine_s3fs?**

Install it for object-native Tigrbl workloads that should share s3fs
configuration and client behavior.

**Who is tigrbl_engine_s3fs for?**

It is for application developers and data engineers integrating Tigrbl with S3
through the fsspec family.

**Where does tigrbl_engine_s3fs fit?**

It is a layer-90 standalone engine package and depends on the public `tigrbl`
facade plus `s3fs`.

**How does tigrbl_engine_s3fs work?**

Its plugin builds an `S3FSEngine` and `S3FSSession`; sessions translate strict
logical object keys into bucket/prefix paths on an `S3FileSystem`.

**Install**

```bash
uv add tigrbl_engine_s3fs
```

**Surface Coverage**

The engine exposes object-oriented session methods rather than pretending that
S3 is a relational database:

- `put_object(key, data)`, `get_object(key)`, `delete_object(key)`
- `object_exists(key)`, `head_object(key)`, `list_objects(prefix="")`
- optional `put_cas(data)`, `get_cas(address)`, `cas_exists(address)`

**Content-addressed storage**

CAS is opt-in with `"cas": True`. `put_cas(payload)` returns a
`sha256:<hex>` address. Objects are stored below `.cas/sha256` by default and
retrieval verifies that the stored bytes still match the requested digest.
Override the physical CAS prefix with `cas_prefix` or disable read verification
with `verify_cas=False` only when verification is performed at another layer.

Transactions are reported as non-atomic because S3 has no multi-object commit.
A session opened with `begin()` stages changes until `commit()` and supports
local rollback, but a remote failure during commit can leave a partial batch.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_engine_s3fs` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_engine_s3fs` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_s3fs/NOTICE) for attribution.
<!-- readme-standards:end notices -->
