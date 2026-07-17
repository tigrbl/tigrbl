<div align="center">
<h1>tigrbl_engine_s3fs</h1>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_engine_s3fs"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl_engine_s3fs"/></a>
</div>

## What is tigrbl_engine_s3fs?

`tigrbl_engine_s3fs` is a standalone Tigrbl object-storage engine backed by
the synchronous `s3fs.S3FileSystem` interface. It supports AWS S3 and S3-
compatible endpoints accepted by `s3fs`.

## Why use tigrbl_engine_s3fs?

Use it when an application already uses the fsspec/s3fs ecosystem or needs a
filesystem-shaped adapter over S3 object storage.

## When should I install tigrbl_engine_s3fs?

Install it for object-native Tigrbl workloads that should share s3fs
configuration and client behavior.

## Who is tigrbl_engine_s3fs for?

It is for application developers and data engineers integrating Tigrbl with S3
through the fsspec family.

## Where does tigrbl_engine_s3fs fit?

It is a layer-90 standalone engine package and depends on the public `tigrbl`
facade plus `s3fs`.

## How does tigrbl_engine_s3fs work?

Its plugin builds an `S3FSEngine` and `S3FSSession`; sessions translate strict
logical object keys into bucket/prefix paths on an `S3FileSystem`.

## Install

```bash
uv add tigrbl_engine_s3fs
```

## Surface Coverage

The engine exposes object-oriented session methods rather than pretending that
S3 is a relational database:

- `put_object(key, data)`, `get_object(key)`, `delete_object(key)`
- `object_exists(key)`, `head_object(key)`, `list_objects(prefix="")`
- optional `put_cas(data)`, `get_cas(address)`, `cas_exists(address)`

## What It Owns

This package owns s3fs-backed object I/O, logical key normalization, local
session staging, and optional SHA-256 content-addressed storage. Its engine
implements the canonical `EngineBase` contract while retaining this
object-specific surface.

## Public API and Import Surface

- `S3FSEngine`
- `S3FSSession`
- `s3fs_engine()` and `s3fs_capabilities()`
- `register()` under the `tigrbl.engine` entry-point group

## Usage Examples

## Configuration

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

## Content-addressed storage

CAS is opt-in with `"cas": True`. `put_cas(payload)` returns a
`sha256:<hex>` address. Objects are stored below `.cas/sha256` by default and
retrieval verifies that the stored bytes still match the requested digest.
Override the physical CAS prefix with `cas_prefix` or disable read verification
with `verify_cas=False` only when verification is performed at another layer.

Transactions are reported as non-atomic because S3 has no multi-object commit.
A session opened with `begin()` stages changes until `commit()` and supports
local rollback, but a remote failure during commit can leave a partial batch.

## How To Choose This Package

Choose this package for the s3fs/fsspec interface. Choose `tigrbl_engine_s3`
when direct access to the boto3 S3 API and its request options is preferable.

## Related Packages

- `tigrbl`
- `tigrbl_engine_s3`

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)

## Support

- [Discord](https://discord.gg/K4YTAPapjR)
- [GitHub Issues](https://github.com/tigrbl/tigrbl/issues)

## Package-local Boundary

This README is the package-local distribution entry point for
`tigrbl_engine_s3fs`. Cross-package claims and release status remain governed
by the repository docs and `.ssot/registry.json`.

## Certification Status

The implementation has package-scoped fake-backend tests and build validation.
It does not claim live AWS or S3-compatible service conformance yet.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
