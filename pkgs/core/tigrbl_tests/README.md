<div align="center">
<h1>tigrbl_tests</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.</strong></p>
<a href="https://pypi.org/project/tigrbl_tests/"><img src="https://img.shields.io/pypi/v/tigrbl_tests?label=PyPI" alt="PyPI version for tigrbl_tests"/></a>
<a href="https://pypi.org/project/tigrbl_tests/"><img src="https://static.pepy.tech/badge/tigrbl_tests" alt="Downloads for tigrbl_tests"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_tests"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_tests/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_tests/README.md.svg?label=hits" alt="Repository hits for tigrbl_tests README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl_tests"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl_tests"/></a>
</div>

## What is tigrbl_tests?

Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.

## Why use tigrbl_tests?

Use it when downstream packages need the same Tigrbl fixtures, conformance helpers, and regression assertions used by the workspace.

## When should I install tigrbl_tests?

Install it in CI, package-local validation, transport integration tests, and compatibility checks.

## Who is tigrbl_tests for?

Maintainers, extension authors, and integration teams validating Tigrbl-compatible packages.

## Where does tigrbl_tests fit?

`tigrbl_tests` lives at `pkgs/core/tigrbl_tests` and serves reusable test, conformance, and integration support for Tigrbl packages.

## How does tigrbl_tests work?

It packages reusable pytest assets and helper modules that exercise public Tigrbl behavior instead of relying on private workspace state.


## Install

```bash
uv add tigrbl_tests
```

```bash
pip install tigrbl_tests
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/) |
| Repository path | [`pkgs/core/tigrbl_tests`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_tests) |
| Python import root | `benchmarks`, `tigrbl_tests`, `triage_tests`, `v4` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl_tests` owns the `test support package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `benchmarks`: comparative_benchmark_verification, open_loop_load_patterns, run_hot_path_perf_suite, tigrbl_fastapi_surface_matrix_benchmark, tigrbl_kernel_plan_benchmark, tigrbl_request_response_benchmark, tigrbl_sse_perf_suite, tigrbl_streaming_perf_suite, tigrbl_websocket_perf_suite, tigrbl_webtransport_perf_suite
- `tigrbl_tests`: examples/, tests/
- `v4`: tests/

## Public API and Import Surface

- Import roots: `benchmarks`, `tigrbl_tests`, `triage_tests`, `v4`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/), [`tigrbl_client`](https://pypi.org/project/tigrbl_client/).
- External runtime dependencies: `psycopg2-binary>=2.9.9`, `asyncpg>=0.30.0`, `pytest>=8.0`, `pytest-asyncio>=0.24.0`, `pytest-xdist>=3.6.1`, `pytest-json-report>=1.5.0`, `python-dotenv`, `requests>=2.32.3`, `flake8>=7.0`, `pytest-timeout>=2.3.1`, `ruff>=0.9.9`, `pytest-benchmark>=4.0.0`, `jinja2>=3.1.0`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl_tests
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl_tests"))
PY
```

### Run packaged Tigrbl tests

```bash
uv run pytest pkgs/core/tigrbl_tests/tests -q
python -m pytest --pyargs tigrbl_tests
```

### Import reusable test helpers

```python
import tigrbl_tests

print(tigrbl_tests.__name__)
```

### Use it in downstream CI

```bash
pip install tigrbl-tests pytest
pytest -q
```

## How To Choose This Package

Choose `tigrbl_tests` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)

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
- Repository: [pkgs/core/tigrbl_tests](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_tests).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl_tests`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
