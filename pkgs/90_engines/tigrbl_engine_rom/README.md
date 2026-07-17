<div align="center">
<h1>tigrbl_engine_rom</h1>
<p><strong>Immutable read-only memory engine plugin for Tigrbl.</strong></p>
<a href="https://pypi.org/project/tigrbl_engine_rom/"><img src="https://img.shields.io/pypi/v/tigrbl_engine_rom?label=PyPI" alt="PyPI version"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python 3.10 | 3.11 | 3.12 | 3.13 | 3.14"/></a>
</div>

## What is tigrbl_engine_rom?

`tigrbl_engine_rom` loads one mapping-backed row image and serves it through Tigrbl's engine-session contract. The engine configuration is bound as an input to a table.

## Why use tigrbl_engine_rom?

Use it for embedded catalogs, fixtures, policy data, reference tables, and other datasets that must never change at runtime.

## When should I install tigrbl_engine_rom?

Install it when your application needs fast reads from a fixed memory image and should fail closed on every write.

## Who is tigrbl_engine_rom for?

It is for application developers shipping trusted reference data or deterministic read-only test images.

## Where does tigrbl_engine_rom fit?

It is a standalone package under `pkgs/90_engines` and is discovered through the `tigrbl.engine` entry-point group as kind `rom`.

## How does tigrbl_engine_rom work?

`ROMEngine` subclasses Tigrbl's `EngineBase`. Construction validates the bound table's rows and primary key, deeply detaches the source data, and freezes it. Reads always return caller-owned copies. Sessions force `read_only=True`, even if a caller requests otherwise.

## Install

```bash
uv add tigrbl_engine_rom
```

## Surface Coverage

| Surface | Value |
|---|---|
| Engine kind | `rom` |
| Python import | `tigrbl_engine_rom` |
| Entry point | `tigrbl.engine` |
| Persistence | process-local immutable memory |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

The package owns the ROM image, read-only session, plugin registration, and scalar result facade.

## Public API and Import Surface

Public symbols are `ROMEngine`, `ROMSession`, `ROMResult`, `build_rom`, `capabilities`, and `register`.

## Usage Examples

```python
from tigrbl_engine_rom import build_rom

engine, sessionmaker = build_rom(mapping={
    "rows": [
        {"code": "US", "name": "United States"},
        {"code": "CA", "name": "Canada"},
    ],
    "primary_key": "code",
})

session = sessionmaker()
assert session.get_row("CA")["name"] == "Canada"
```

Bind the engine configuration into a table:

```python
from tigrbl.factories.table import defineTableSpec

class CountrySpec(defineTableSpec(engine={
    "kind": "rom",
    "rows": [
        {"code": "US", "name": "United States"},
        {"code": "CA", "name": "Canada"},
    ],
    "primary_key": "code",
})):
    pass
```

## How To Choose This Package

Choose ROM for immutable embedded data. Choose `tigrbl_engine_inmemory` when transactions and runtime writes are required.

## Related Packages

- `tigrbl`
- `tigrbl_engine_inmemory`
- `tigrbl_engine_memkv`

## Documentation Links

- [Workspace docs](../../../docs/README.md)
- [Package catalog](../../../docs/developer/PACKAGE_CATALOG.md)
- [SSOT registry](../../../.ssot/registry.json)

## Support

- [Discord](https://discord.gg/K4YTAPapjR)
- [GitHub issues](https://github.com/tigrbl/tigrbl/issues)

## Certification Status

The package is implemented with package-local behavioral tests. Certification remains governed by the repository SSOT registry and release workflows.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
