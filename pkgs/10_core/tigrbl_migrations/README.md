# tigrbl-migrations

Generic component manifests, migration DAGs, schema ownership, ledgers, and
deployment locks for Tigrbl storage packages.

The package deliberately contains no identity-specific tables and does not
discover every installed component implicitly. Applications compose explicit
`StorageManifest` instances, validate their dependency and ownership graph,
and ask `MigrationOrchestrator` for a deterministic plan.

Manifest format compatibility is governed independently from the Python
artifact version by `[tool.tigrbl.manifest].version` in `pyproject.toml`.


## What is tigrbl-migrations?

Component manifests, migration DAGs, schema ownership, ledgers, and deployment locks for Tigrbl.

## Why use tigrbl-migrations?

Use this project for component manifests, migration DAGs, schema ownership, ledgers, and deployment locks for Tigrbl.

## When should I install tigrbl-migrations?

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

## Who is tigrbl-migrations for?

Tigrbl maintainers and application developers working with this project’s APIs.

## Where does tigrbl-migrations fit?

Source: `pkgs/10_core/tigrbl_migrations` in the Tigrbl workspace.

## How does tigrbl-migrations work?

StorageManifest, Migration, MigrationOrchestrator, and StorageComposition. The examples and implementation above describe the configuration and execution flow.

## Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

## Install

From the repository root:

```console
uv sync --project pkgs/10_core/tigrbl_migrations
```

## Surface Coverage

| Surface | Value |
| --- | --- |
| Project | `tigrbl-migrations` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_migrations` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

## What It Owns

Component manifests, migration DAGs, schema ownership, ledgers, and deployment locks for Tigrbl.

## Public API and Import Surface

StorageManifest, Migration, MigrationOrchestrator, and StorageComposition. See the project source and existing examples above for supported call signatures.

## Usage Examples

The walkthrough above is retained. The entry surface can be loaded with:

```python
from tigrbl_migrations import StorageManifest, Migration
```

## How To Choose This Package

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

## Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

## Documentation Links

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/10_core/tigrbl_migrations)

## Support

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

## License

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)
