"""Reusable conformance assertions for downstream storage packages."""

from __future__ import annotations

from typing import Iterable

from .composition import StorageComposition
from .manifests import StorageManifest, validate_unique_objects
from .migration import Migration


def assert_manifest_valid(manifest: StorageManifest) -> None:
    StorageManifest.from_mapping(manifest.canonical_mapping())


def assert_single_release_head(
    manifest: StorageManifest, migrations: Iterable[Migration]
) -> None:
    graph = StorageComposition.from_manifests(manifest).graph(migrations)
    graph.validate_release_head(
        component=manifest.component_id, declared_head=manifest.migration_head
    )


def assert_migration_graph_valid(
    composition: StorageComposition, migrations: Iterable[Migration]
) -> None:
    composition.graph(migrations).topological_order()


def assert_ownership_exclusive(composition: StorageComposition) -> None:
    validate_unique_objects(composition.manifests)
