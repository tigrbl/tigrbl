<div align="center">
<h1>tigrbl_engine_s3</h1>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_engine_s3"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl_engine_s3"/></a>
</div>

## What is tigrbl_engine_s3?

`tigrbl_engine_s3` is a standalone Tigrbl object-storage engine that calls the
S3 API directly through a boto3-compatible client. It supports AWS S3 and S3-
compatible services such as MinIO or R2 when configured with an endpoint URL.

## Why use tigrbl_engine_s3?

Use it when an application needs direct S3 request semantics, credential-chain
behavior, endpoint configuration, or server-side upload options.

## When should I install tigrbl_engine_s3?

Install it for object-native Tigrbl workloads that should communicate through a
boto3-compatible S3 client.

## Who is tigrbl_engine_s3 for?

It is for application developers and platform engineers integrating Tigrbl with
AWS S3 or an S3-compatible service.

## Where does tigrbl_engine_s3 fit?

It is a layer-90 standalone engine package and depends on the public `tigrbl`
facade plus `boto3`.

## How does tigrbl_engine_s3 work?

Its plugin builds an `S3Engine` and `S3Session`; sessions translate strict
logical object keys into direct `put_object`, `get_object`, and related calls.

## Install

```bash
uv add tigrbl_engine_s3
```

## Surface Coverage

The session API is object-native:

- `put_object(key, data)`, `get_object(key)`, `delete_object(key)`
- `object_exists(key)`, `head_object(key)`, `list_objects(prefix="")`
- optional `put_cas(data)`, `get_cas(address)`, `cas_exists(address)`

## What It Owns

This package owns direct S3 object I/O, logical key normalization, local session
staging, upload options, and optional SHA-256 content-addressed storage. Its
engine implements the canonical `EngineBase` contract while retaining this
object-specific surface.

## Public API and Import Surface

- `S3Engine`
- `S3Session`
- `s3_engine()` and `s3_capabilities()`
- `register()` under the `tigrbl.engine` entry-point group

## Usage Examples

## Configuration

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

## Content-addressed storage

CAS is opt-in with `"cas": True`. The returned address is `sha256:<hex>` and
the physical object is sharded below `.cas/sha256` by default. Retrieval hashes
the received bytes and fails if they do not match the requested address.

S3 is not a multi-object transactional store. `begin()` provides local staging
and rollback before upload, but `commit()` is a sequence of remote S3 calls and
can be partially applied if a later request fails.

## How To Choose This Package

Choose this package for direct boto3-compatible S3 calls. Choose
`tigrbl_engine_s3fs` when the fsspec/s3fs filesystem interface is preferable.

## Related Packages

- `tigrbl`
- `tigrbl_engine_s3fs`

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
`tigrbl_engine_s3`. Cross-package claims and release status remain governed by
the repository docs and `.ssot/registry.json`.

## Certification Status

The implementation has package-scoped fake-backend tests and build validation.
It does not claim live AWS or S3-compatible service conformance yet.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
