"""Immutable migration declarations and deterministic directed acyclic graphs."""

from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass
from enum import Enum
from graphlib import CycleError, TopologicalSorter
from typing import Any, Callable, Iterable, Mapping

from .errors import GraphError, ManifestError

MigrationCallable = Callable[[Any], None]


class MigrationKind(str, Enum):
    STANDARD = "standard"
    ADOPT = "adopt"
    TRANSFER = "transfer"


@dataclass(frozen=True, slots=True)
class Migration:
    revision: str
    component: str
    parents: tuple[str, ...] = ()
    kind: MigrationKind = MigrationKind.STANDARD
    reversible: bool = False
    upgrade: MigrationCallable | None = None
    downgrade: MigrationCallable | None = None
    adopted_objects: tuple[str, ...] = ()
    transfer_source: str | None = None
    transfer_destination: str | None = None
    transferred_objects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.kind, str):
            try:
                object.__setattr__(self, "kind", MigrationKind(self.kind))
            except ValueError as exc:
                raise GraphError(f"unsupported migration kind: {self.kind}") from exc
        if not self.revision.strip() or not self.component.strip():
            raise GraphError("migration revision and component are required")
        if len(self.parents) != len(set(self.parents)):
            raise GraphError(f"migration {self.revision} repeats a parent")
        if self.revision in self.parents:
            raise GraphError(f"migration {self.revision} cannot depend on itself")
        if self.reversible != (self.downgrade is not None):
            raise GraphError(
                f"migration {self.revision} reversibility must match downgrade availability"
            )
        if self.kind is MigrationKind.STANDARD and self.upgrade is None:
            raise GraphError(f"standard migration {self.revision} requires an upgrade")
        if self.kind is MigrationKind.ADOPT and not self.adopted_objects:
            raise GraphError(f"adoption migration {self.revision} requires adopted objects")
        if self.kind is MigrationKind.TRANSFER:
            if not self.transfer_source or not self.transfer_destination or not self.transferred_objects:
                raise GraphError(
                    f"transfer migration {self.revision} requires source, destination, and objects"
                )
            if self.transfer_source == self.transfer_destination:
                raise GraphError("transfer source and destination must differ")

    def checksum(self) -> str:
        parts = [
            self.component,
            self.revision,
            self.kind.value,
            ",".join(self.parents),
            str(self.reversible),
            _callable_source(self.upgrade),
            _callable_source(self.downgrade),
            ",".join(self.adopted_objects),
            self.transfer_source or "",
            self.transfer_destination or "",
            ",".join(self.transferred_objects),
        ]
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _callable_source(value: MigrationCallable | None) -> str:
    if value is None:
        return ""
    try:
        return inspect.getsource(value)
    except (OSError, TypeError):
        code = getattr(value, "__code__", None)
        return repr((getattr(value, "__module__", ""), getattr(value, "__qualname__", ""), code))


class MigrationGraph:
    def __init__(self, migrations: Iterable[Migration] = ()) -> None:
        self._migrations: dict[str, Migration] = {}
        self._external_edges: dict[str, set[str]] = {}
        for migration in migrations:
            self.add(migration)

    @property
    def migrations(self) -> Mapping[str, Migration]:
        return dict(self._migrations)

    def add(self, migration: Migration) -> None:
        prior = self._migrations.get(migration.revision)
        if prior is not None:
            if prior != migration or prior.checksum() != migration.checksum():
                raise GraphError(f"revision {migration.revision} has conflicting declarations")
            return
        self._migrations[migration.revision] = migration

    def add_requirement_edge(self, *, revision: str, required_revision: str) -> None:
        self._external_edges.setdefault(revision, set()).add(required_revision)

    def _dependencies(self) -> dict[str, set[str]]:
        result = {
            revision: set(migration.parents) | self._external_edges.get(revision, set())
            for revision, migration in self._migrations.items()
        }
        missing = sorted({parent for parents in result.values() for parent in parents} - set(result))
        if missing:
            raise GraphError(f"migration graph references missing revisions: {missing}")
        return result

    def topological_order(self) -> tuple[str, ...]:
        dependencies = self._dependencies()
        try:
            sorter = TopologicalSorter(dependencies)
            sorter.prepare()
        except CycleError as exc:
            raise GraphError(f"migration graph contains a cycle: {exc.args[1]}") from exc
        ordered: list[str] = []
        while sorter.is_active():
            ready = sorted(sorter.get_ready())
            ordered.extend(ready)
            sorter.done(*ready)
        return tuple(ordered)

    def closure(self, revision: str) -> frozenset[str]:
        dependencies = self._dependencies()
        if revision not in dependencies:
            raise GraphError(f"unknown migration revision: {revision}")
        found: set[str] = set()
        stack = [revision]
        while stack:
            current = stack.pop()
            if current in found:
                continue
            found.add(current)
            stack.extend(dependencies[current])
        return frozenset(found)

    def component_heads(self, component: str) -> tuple[str, ...]:
        owned = {rev for rev, item in self._migrations.items() if item.component == component}
        parents = {
            parent
            for rev in owned
            for parent in self._migrations[rev].parents
            if parent in owned
        }
        return tuple(sorted(owned - parents))

    def validate_release_head(self, *, component: str, declared_head: str) -> None:
        heads = self.component_heads(component)
        if heads != (declared_head,):
            raise GraphError(
                f"component {component} declares {declared_head}, but graph heads are {heads}"
            )

    def attach_manifest_requirements(self, manifests: Iterable[Any]) -> None:
        manifests = tuple(manifests)
        by_component = {item.component_id: item for item in manifests}
        for manifest in manifests:
            self.validate_release_head(
                component=manifest.component_id, declared_head=manifest.migration_head
            )
            roots = [
                migration.revision
                for migration in self._migrations.values()
                if migration.component == manifest.component_id and not migration.parents
            ]
            for requirement in manifest.requires:
                dependency = by_component.get(requirement.component)
                if dependency is None:
                    raise ManifestError(
                        f"component {manifest.component_id} requires missing {requirement.component}"
                    )
                if not requirement.accepts(dependency.schema_contract):
                    raise ManifestError(
                        f"component {dependency.component_id} contract {dependency.schema_contract} "
                        f"does not satisfy {requirement.contract}"
                    )
                if requirement.minimum_revision not in self.closure(dependency.migration_head):
                    raise GraphError(
                        f"required revision {requirement.minimum_revision} is not in "
                        f"{dependency.component_id} head closure"
                    )
                for root in roots:
                    self.add_requirement_edge(
                        revision=root, required_revision=requirement.minimum_revision
                    )


@dataclass(frozen=True, slots=True)
class MigrationPlan:
    ordered: tuple[Migration, ...]
    already_applied: tuple[str, ...]
    forward_only: tuple[str, ...]
    resulting_heads: Mapping[str, str]


def build_plan(
    graph: MigrationGraph,
    *,
    applied: Iterable[str],
    declared_heads: Mapping[str, str],
) -> MigrationPlan:
    applied_set = set(applied)
    unknown = applied_set - set(graph.migrations)
    if unknown:
        raise GraphError(f"ledger contains unknown revisions: {sorted(unknown)}")
    order = graph.topological_order()
    pending = tuple(graph.migrations[revision] for revision in order if revision not in applied_set)
    return MigrationPlan(
        ordered=pending,
        already_applied=tuple(revision for revision in order if revision in applied_set),
        forward_only=tuple(item.revision for item in pending if not item.reversible),
        resulting_heads=dict(declared_heads),
    )
