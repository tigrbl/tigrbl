<div align="center">
<h1>tigrbl-ops-realtime</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Realtime, streaming, datagram, websocket, and event operation handlers for Tigrbl ASGI runtimes.</strong></p>
<a href="https://pypi.org/project/tigrbl-ops-realtime/"><img src="https://img.shields.io/pypi/v/tigrbl-ops-realtime?label=PyPI" alt="PyPI version for tigrbl-ops-realtime"/></a>
<a href="https://pypi.org/project/tigrbl-ops-realtime/"><img src="https://static.pepy.tech/badge/tigrbl-ops-realtime" alt="Downloads for tigrbl-ops-realtime"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-ops-realtime"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_ops_realtime/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_ops_realtime/README.md.svg?label=hits" alt="Repository hits for tigrbl-ops-realtime README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-ops-realtime"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-ops-realtime"/></a>
</div>

## What is tigrbl-ops-realtime?

Realtime, streaming, datagram, websocket, and event operation handlers for Tigrbl ASGI runtimes.

## Why use tigrbl-ops-realtime?

Use it when you need this operation-family boundary directly instead of consuming operations through the top-level facade.

## When should I install tigrbl-ops-realtime?

Install it for framework internals, extension packages, or focused tests that target this operation plane.

## Who is tigrbl-ops-realtime for?

Framework maintainers and extension authors working near Tigrbl operation dispatch.

## Where does tigrbl-ops-realtime fit?

`tigrbl-ops-realtime` lives at `pkgs/core/tigrbl_ops_realtime` and serves focused operation dispatch behavior inside the Tigrbl runtime model.

## How does tigrbl-ops-realtime work?

It contributes operation handlers and dispatch-facing primitives consumed by the facade, runtime, and kernel layers.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl-ops-realtime
```

```bash
pip install tigrbl-ops-realtime
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/) |
| Repository path | [`pkgs/core/tigrbl_ops_realtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_realtime) |
| Python import root | `tigrbl_ops_realtime` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl-ops-realtime` owns the `operation-family package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_ops_realtime`: ops

## Public API and Import Surface

- Import roots: `tigrbl_ops_realtime`.
- Public symbols: `append_chunk`, `checkpoint`, `download`, `publish`, `send_datagram`, `subscribe`, `tail`, `upload`.
- Workspace dependencies: none declared.
- External runtime dependencies: none declared.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-ops-realtime
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-ops-realtime"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_ops_realtime")
print(module.__name__)
```

### Import a public symbol

```python
from tigrbl_ops_realtime import append_chunk

print(append_chunk)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-ops-realtime
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-ops-realtime` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/core/tigrbl_ops_realtime](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_realtime).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl-ops-realtime`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
