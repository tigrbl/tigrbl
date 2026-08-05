"""Explicit storage-component composition and ownership validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .errors import ManifestError
from .manifests import StorageManifest, validate_unique_objects
from .migration import Migration, MigrationGraph


@dataclass(frozen=True, slots=True)
class StorageComposition:
    manifests: tuple[StorageManifest, ...]

    @classmethod
    def from_manifests(cls, *manifests: StorageManifest) -> "StorageComposition":
        if not manifests:
            raise ManifestError("a storage composition requires at least one manifest")
        component_ids = [item.component_id for item in manifests]
        if len(component_ids) != len(set(component_ids)):
            raise ManifestError("storage composition repeats a component")
        ordered = tuple(sorted(manifests, key=lambda item: item.component_id))
        validate_unique_objects(ordered)
        by_component = {item.component_id: item for item in ordered}
        for manifest in ordered:
            for requirement in manifest.requires:
                dependency = by_component.get(requirement.component)
                if dependency is None:
                    raise ManifestError(
                        f"component {manifest.component_id} requires missing {requirement.component}"
                    )
                if not requirement.accepts(dependency.schema_contract):
                    raise ManifestError(
                        f"component {manifest.component_id} requires {requirement.component} "
                        f"contract {requirement.contract}; selected contract is "
                        f"{dependency.schema_contract}"
                    )
        return cls(manifests=ordered)

    @property
    def by_component(self) -> Mapping[str, StorageManifest]:
        return {item.component_id: item for item in self.manifests}

    @property
    def declared_heads(self) -> Mapping[str, str]:
        return {item.component_id: item.migration_head for item in self.manifests}

    def graph(self, migrations: Iterable[Migration]) -> MigrationGraph:
        graph = MigrationGraph(migrations)
        graph.attach_manifest_requirements(self.manifests)
        graph.topological_order()
        return graph
