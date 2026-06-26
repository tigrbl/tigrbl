<div align="center">
<h1>tigrbl-ops-webtransport</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>WebTransport control-plane operation handlers for Tigrbl stream and session coordination.</strong></p>
<a href="https://pypi.org/project/tigrbl-ops-webtransport/"><img src="https://img.shields.io/pypi/v/tigrbl-ops-webtransport?label=PyPI" alt="PyPI version for tigrbl-ops-webtransport"/></a>
<a href="https://pypi.org/project/tigrbl-ops-webtransport/"><img src="https://static.pepy.tech/badge/tigrbl-ops-webtransport" alt="Downloads for tigrbl-ops-webtransport"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-ops-webtransport"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_ops_webtransport/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_ops_webtransport/README.md.svg?label=hits" alt="Repository hits for tigrbl-ops-webtransport README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-ops-webtransport"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-ops-webtransport"/></a>
</div>

## What is tigrbl-ops-webtransport?

WebTransport control-plane operation handlers for Tigrbl stream and session coordination.

## Why use tigrbl-ops-webtransport?

Use it when WebTransport stream lifecycle commands need a focused operation-family boundary instead of being embedded in realtime payload handlers or runtime code.

## When should I install tigrbl-ops-webtransport?

Install it for framework internals, extension packages, or focused tests that target WebTransport control-plane operation dispatch.

## Who is tigrbl-ops-webtransport for?

Framework maintainers and extension authors working near WebTransport operation planning and control-plane dispatch.

## Where does tigrbl-ops-webtransport fit?

`tigrbl-ops-webtransport` lives at `pkgs/core/tigrbl_ops_webtransport` and owns control-plane commands such as opening and closing WebTransport streams and sessions.

## How does tigrbl-ops-webtransport work?

It returns structured control-plane command payloads that atoms and runtime projections can pass toward the delegated WebTransport server stack.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl-ops-webtransport
```

```bash
pip install tigrbl-ops-webtransport
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/) |
| Repository path | [`pkgs/core/tigrbl_ops_webtransport`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_webtransport) |
| Python import root | `tigrbl_ops_webtransport` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl-ops-webtransport` owns the `operation-family package` boundary for WebTransport control-plane commands. It does not own HTTP/3, QUIC, TLS, stream scheduling, or server-stack conformance.

Implementation orientation:
- `tigrbl_ops_webtransport`: ops

## Public API and Import Surface

- Import roots: `tigrbl_ops_webtransport`.
- Public symbols: `open_bidi_stream`, `open_unidi_stream`, `close_stream`, `close_session`.
- Workspace dependencies: none declared.
- External runtime dependencies: none declared.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-ops-webtransport
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-ops-webtransport"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_ops_webtransport")
print(module.__name__)
```

### Import a public symbol

```python
from tigrbl_ops_webtransport import open_bidi_stream

print(open_bidi_stream)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-ops-webtransport
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-ops-webtransport` when you need WebTransport stream/session control-plane commands directly. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/) for publish, subscribe, tail, upload, download, chunk, datagram, and checkpoint operation handlers.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)

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
- Repository: [pkgs/core/tigrbl_ops_webtransport](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_webtransport).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl-ops-webtransport`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
