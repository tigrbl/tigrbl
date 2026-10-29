# tigrbl_engine_mariadb

The MariaDB engine plugin for Tigrbl. It registers the `mariadb` engine kind and
returns Tigrbl `EngineSession` instances backed by SQLAlchemy and PyMySQL.

```python
from tigrbl.factories.engine import mariadb

engine = mariadb(user="portwyrm", pwd="secret", name="portwyrm")
```



## What is tigrbl_engine_mariadb?

MariaDB engine plugin providing native Tigrbl EngineSession integration.

## Why use tigrbl_engine_mariadb?

Use this project for mariaDB engine plugin providing native Tigrbl EngineSession integration.

## When should I install tigrbl_engine_mariadb?

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

## Who is tigrbl_engine_mariadb for?

Tigrbl maintainers and application developers working with this project’s APIs.

## Where does tigrbl_engine_mariadb fit?

Source: `pkgs/90_engines/tigrbl_engine_mariadb` in the Tigrbl workspace.

## How does tigrbl_engine_mariadb work?

MariaDB/MySQL engine registration via tigrbl.engine_plugins. The examples and implementation above describe the configuration and execution flow.

## Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

## Install

From the repository root:

```console
uv sync --project pkgs/90_engines/tigrbl_engine_mariadb
```

## Surface Coverage

| Surface | Value |
| --- | --- |
| Project | `tigrbl_engine_mariadb` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_engine_mariadb` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

## What It Owns

MariaDB engine plugin providing native Tigrbl EngineSession integration.

## Public API and Import Surface

MariaDB/MySQL engine registration via tigrbl.engine_plugins. See the project source and existing examples above for supported call signatures.

## Usage Examples

The walkthrough above is retained. The entry surface can be loaded with:

```python
from tigrbl.factories.engine import mariadb
```

## How To Choose This Package

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

## Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

## Documentation Links

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_mariadb)

## Support

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

## License

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)
