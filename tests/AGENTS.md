# Finding Tigrbl tests

- The [shared Tigrbl suite](../pkgs/210_tests/tigrbl_tests/tests/) contains unit, integration (`i9n`), architecture, protocol, security, and performance tests. See the [test layer guide](../pkgs/210_tests/AGENTS.md) for its layout.
- For behavior owned by one workspace package, look in that package’s `tests/` directory under `pkgs/`.
- This directory contains [planned contract tests](planned/) and [SSOT proof scaffolding](ssot_scaffold/).
- CI and release tooling have their own suites in [`tools/ci/tests/`](../tools/ci/tests/) and [`tools/release/tests/`](../tools/release/tests/).

From the repository root, pass the relevant test directory or file to `uv run pytest`. The [root pytest configuration](../pyproject.toml) lists the default collection paths.
