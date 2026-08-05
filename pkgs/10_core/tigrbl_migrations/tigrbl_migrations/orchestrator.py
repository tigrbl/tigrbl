"""Composition-aware planning and execution over a migration ledger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .composition import StorageComposition
from .errors import MigrationError
from .ledger import MigrationLedger
from .migration import Migration, MigrationGraph, MigrationKind, MigrationPlan, build_plan


@dataclass(slots=True)
class MigrationOrchestrator:
    composition: StorageComposition
    migrations: tuple[Migration, ...]
    ledger: MigrationLedger
    artifact_versions: Mapping[str, str]

    def graph(self) -> MigrationGraph:
        return self.composition.graph(self.migrations)

    def plan(self) -> MigrationPlan:
        return build_plan(
            self.graph(),
            applied=self.ledger.applied_revisions(),
            declared_heads=self.composition.declared_heads,
        )

    def apply(self, *, acknowledge_forward_only: bool = False) -> MigrationPlan:
        self.ledger.bootstrap()
        plan = self.plan()
        if plan.forward_only and not acknowledge_forward_only:
            raise MigrationError(
                "forward-only migrations require acknowledgement: " + ", ".join(plan.forward_only)
            )
        execution_id = self.ledger.acquire_lock()
        try:
            by_component = self.composition.by_component
            for migration in plan.ordered:
                manifest = by_component[migration.component]
                if migration.kind is MigrationKind.STANDARD:
                    assert migration.upgrade is not None
                    migration.upgrade(self.ledger.connection)
                    mode = "executed"
                elif migration.kind is MigrationKind.ADOPT:
                    mode = "adopted"
                else:
                    assert migration.transfer_source and migration.transfer_destination
                    self.ledger.transfer_objects(
                        migration.transferred_objects,
                        source=migration.transfer_source,
                        destination=migration.transfer_destination,
                        revision=migration.revision,
                    )
                    mode = "transferred"
                self.ledger.record_migration(
                    migration,
                    artifact_version=self.artifact_versions[migration.component],
                    execution_id=execution_id,
                    application_mode=mode,
                )
                if migration.kind is not MigrationKind.TRANSFER:
                    self.ledger.claim_objects(
                        manifest,
                        revision=migration.revision,
                        state="active",
                    )
            for manifest in self.composition.manifests:
                self.ledger.record_component(
                    manifest,
                    artifact_version=self.artifact_versions[manifest.component_id],
                )
            return plan
        finally:
            self.ledger.release_lock(execution_id)
