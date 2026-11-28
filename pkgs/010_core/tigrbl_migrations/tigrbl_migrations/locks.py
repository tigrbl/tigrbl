"""Deterministic deployment-lock models and TOML rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

from .composition import StorageComposition
from .errors import LockError
from .version import require_semver


@dataclass(frozen=True, slots=True)
class LockedComponent:
    component_id: str
    distribution: str
    artifact: str
    schema_contract: str
    migration_head: str
    manifest_digest: str


@dataclass(frozen=True, slots=True)
class DeploymentLock:
    lock_version: str
    components: tuple[LockedComponent, ...]

    @classmethod
    def from_composition(
        cls,
        composition: StorageComposition,
        *,
        artifact_versions: dict[str, str],
        lock_version: str = "1.0.0",
    ) -> "DeploymentLock":
        require_semver(lock_version, field="deployment lock version")
        rows = []
        for manifest in composition.manifests:
            rows.append(
                LockedComponent(
                    component_id=manifest.component_id,
                    distribution=manifest.distribution,
                    artifact=artifact_versions[manifest.component_id],
                    schema_contract=manifest.schema_contract,
                    migration_head=manifest.migration_head,
                    manifest_digest=manifest.digest(),
                )
            )
        return cls(lock_version=lock_version, components=tuple(rows))

    def to_toml(self) -> str:
        lines = [f'lock_version = "{self.lock_version}"', ""]
        for item in sorted(self.components, key=lambda row: row.component_id):
            lines.extend(
                [
                    f'[components."{item.component_id}"]',
                    f'distribution = "{item.distribution}"',
                    f'artifact = "{item.artifact}"',
                    f'schema_contract = "{item.schema_contract}"',
                    f'migration_head = "{item.migration_head}"',
                    f'manifest_digest = "{item.manifest_digest}"',
                    "",
                ]
            )
        return "\n".join(lines)

    @classmethod
    def from_text(cls, value: str) -> "DeploymentLock":
        try:
            data = tomllib.loads(value)
            require_semver(data["lock_version"], field="deployment lock version")
            components = tuple(
                LockedComponent(
                    component_id=component_id,
                    distribution=row["distribution"],
                    artifact=row["artifact"],
                    schema_contract=row["schema_contract"],
                    migration_head=row["migration_head"],
                    manifest_digest=row["manifest_digest"],
                )
                for component_id, row in sorted(data["components"].items())
            )
            return cls(lock_version=data["lock_version"], components=components)
        except (KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
            raise LockError("invalid deployment lock") from exc

    @classmethod
    def from_toml(cls, path: str | Path) -> "DeploymentLock":
        return cls.from_text(Path(path).read_text(encoding="utf-8"))

    def verify(
        self,
        composition: StorageComposition,
        *,
        artifact_versions: dict[str, str],
    ) -> None:
        expected = DeploymentLock.from_composition(
            composition,
            artifact_versions=artifact_versions,
            lock_version=self.lock_version,
        )
        if self != expected:
            raise LockError("deployment lock does not match the selected storage composition")
