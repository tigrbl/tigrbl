# tigrbl-migrations

Generic component manifests, migration DAGs, schema ownership, ledgers, and
deployment locks for Tigrbl storage packages.

The package deliberately contains no identity-specific tables and does not
discover every installed component implicitly. Applications compose explicit
`StorageManifest` instances, validate their dependency and ownership graph,
and ask `MigrationOrchestrator` for a deterministic plan.

Manifest format compatibility is governed independently from the Python
artifact version by `[tool.tigrbl.manifest].version` in `pyproject.toml`.
