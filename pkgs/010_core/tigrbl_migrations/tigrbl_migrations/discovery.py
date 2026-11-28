"""Explicit manifest and migration-package discovery."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable

from .errors import ManifestError
from .manifests import StorageManifest
from .migration import Migration


def discover_manifest(import_root: str) -> StorageManifest:
    module = importlib.import_module(import_root)
    manifest = getattr(module, "MANIFEST", None)
    if not isinstance(manifest, StorageManifest):
        raise ManifestError(f"{import_root} does not export a StorageManifest as MANIFEST")
    return manifest


def discover_migrations(manifest: StorageManifest) -> tuple[Migration, ...]:
    package = importlib.import_module(manifest.migrations_package)
    found: list[Migration] = []
    for module_info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        migration = getattr(importlib.import_module(module_info.name), "MIGRATION", None)
        if not isinstance(migration, Migration):
            raise ManifestError(f"{module_info.name} does not export MIGRATION")
        if migration.component != manifest.component_id:
            raise ManifestError(
                f"{module_info.name} belongs to {migration.component}, expected {manifest.component_id}"
            )
        found.append(migration)
    return tuple(sorted(found, key=lambda item: item.revision))


def discover_components(import_roots: Iterable[str]) -> tuple[tuple[StorageManifest, ...], tuple[Migration, ...]]:
    manifests = tuple(discover_manifest(root) for root in import_roots)
    migrations = tuple(item for manifest in manifests for item in discover_migrations(manifest))
    return manifests, migrations
