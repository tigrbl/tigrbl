<div align="center">
<h1>tigrbl_tests</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.</strong></p>
<a href="https://pypi.org/project/tigrbl_tests/"><img src="https://img.shields.io/pypi/v/tigrbl_tests?label=PyPI" alt="PyPI version for tigrbl_tests"/></a>
<a href="https://pypi.org/project/tigrbl_tests/"><img src="https://static.pepy.tech/badge/tigrbl_tests" alt="Downloads for tigrbl_tests"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_tests/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_tests/README.md.svg?label=hits" alt="Repository hits for tigrbl_tests README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl_tests"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl_tests"/></a>
</div>

## Install

```bash
uv add tigrbl_tests
```

```bash
pip install tigrbl_tests
```

## What It Owns

`tigrbl_tests` owns the tests boundary inside the split Python workspace. Key implementation roots include `benchmarks` with `comparative_benchmark_verification, open_loop_load_patterns, run_hot_path_perf_suite, tigrbl_fastapi_surface_matrix_benchmark, tigrbl_kernel_plan_benchmark, tigrbl_request_response_benchmark`; `examples` with `01-beginner-foundations/, 01_beginner_fundamentals/, 02-beginner-columns/, 02_beginner_models/, 03-beginner-mixins/, 03_beginner_specs/`.

## Use It When

Use `tigrbl_tests` when you need reusable fixtures, conformance helpers, parity assets, and benchmark-oriented test surfaces for Tigrbl packages or downstream integrations.

## Public Surface

- Primary module root: `benchmarks` with module families `comparative_benchmark_verification, open_loop_load_patterns, run_hot_path_perf_suite, tigrbl_fastapi_surface_matrix_benchmark, tigrbl_kernel_plan_benchmark, tigrbl_request_response_benchmark, tigrbl_sse_perf_suite, tigrbl_streaming_perf_suite`.
- Primary module root: `examples` with module families `01-beginner-foundations/, 01_beginner_fundamentals/, 02-beginner-columns/, 02_beginner_models/, 03-beginner-mixins/, 03_beginner_specs/, 04-beginner-app-api/, 04_beginner_tables_columns/`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_tests`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `benchmarks` modules: `comparative_benchmark_verification, open_loop_load_patterns, run_hot_path_perf_suite, tigrbl_fastapi_surface_matrix_benchmark, tigrbl_kernel_plan_benchmark, tigrbl_request_response_benchmark, tigrbl_sse_perf_suite, tigrbl_streaming_perf_suite, tigrbl_websocket_perf_suite, tigrbl_webtransport_perf_suite`.
- `examples` modules: `01-beginner-foundations/, 01_beginner_fundamentals/, 02-beginner-columns/, 02_beginner_models/, 03-beginner-mixins/, 03_beginner_specs/, 04-beginner-app-api/, 04_beginner_tables_columns/, 05-beginner-usage/, 05_beginner_app_api/`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/), [`tigrbl_client`](https://pypi.org/project/tigrbl_client/).
- External runtime dependencies: `psycopg2-binary>=2.9.9`, `asyncpg>=0.30.0`, `pytest>=8.0`, `pytest-asyncio>=0.24.0`, `pytest-xdist>=3.6.1`, `pytest-json-report>=1.5.0`, `python-dotenv`, `requests>=2.32.3`, `flake8>=7.0`, `pytest-timeout>=2.3.1`.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)

## Canonical Repository Docs

- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package-local Boundary

This file is a package-local distribution entry point.
Use this page for package installation and boundary orientation. Repository governance, conformance state, target status, and release evidence remain governed from `docs/` and `.ssot/`.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
