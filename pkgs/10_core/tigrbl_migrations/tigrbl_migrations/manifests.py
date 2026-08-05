"""Python and TOML contracts for component-owned storage schemas."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from .errors import ManifestError
from .version import require_semver, require_supported_manifest_version

_COMPONENT_ID = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9][a-z0-9-]*)+$")
_OBJECT_ID = re.compile(r"^[a-z][a-z0-9_]*(?:[.:-][a-z0-9_][a-z0-9_-]*)+$")
_PHYSICAL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?$")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class DatabaseObject:
    id: str
    kind: str
    physical_name: str
    model: str | None = None

    def __post_init__(self) -> None:
        if _OBJECT_ID.fullmatch(self.id) is None:
            raise ManifestError(f"invalid database object id: {self.id!r}")
        if self.kind not in {"table", "index", "constraint", "view"}:
            raise ManifestError(f"unsupported database object kind: {self.kind!r}")
        if _PHYSICAL_NAME.fullmatch(self.physical_name) is None:
            raise ManifestError(f"invalid physical database object name: {self.physical_name!r}")
        if self.model is not None and ":" not in self.model:
            raise ManifestError("model references must use 'module:attribute' syntax")


@dataclass(frozen=True, slots=True)
class SchemaRequirement:
    component: str
    contract: str
    minimum_revision: str

    def __post_init__(self) -> None:
        if _COMPONENT_ID.fullmatch(self.component) is None:
            raise ManifestError(f"invalid required component id: {self.component!r}")
        try:
            SpecifierSet(self.contract)
        except InvalidSpecifier as exc:
            raise ManifestError(f"invalid schema contract requirement: {self.contract!r}") from exc
        _require_string(self.minimum_revision, "minimum_revision")

    def accepts(self, contract: str) -> bool:
        try:
            parsed = Version(contract)
        except InvalidVersion as exc:
            raise ManifestError(f"invalid component schema contract: {contract!r}") from exc
        return parsed in SpecifierSet(self.contract)


@dataclass(frozen=True, slots=True)
class ComponentManifest:
    manifest_version: str
    component_id: str
    distribution: str
    import_root: str

    def __post_init__(self) -> None:
        require_supported_manifest_version(self.manifest_version)
        if _COMPONENT_ID.fullmatch(self.component_id) is None:
            raise ManifestError(f"invalid component id: {self.component_id!r}")
        _require_string(self.distribution, "distribution")
        _require_string(self.import_root, "import_root")

    def installed_artifact_version(self) -> str:
        try:
            return importlib.metadata.version(self.distribution)
        except importlib.metadata.PackageNotFoundError as exc:
            raise ManifestError(f"distribution is not installed: {self.distribution}") from exc


@dataclass(frozen=True, slots=True)
class StorageManifest(ComponentManifest):
    schema_contract: str
    migration_head: str
    migrations_package: str
    objects: tuple[DatabaseObject, ...] = ()
    requires: tuple[SchemaRequirement, ...] = ()

    def __post_init__(self) -> None:
        super(StorageManifest, self).__post_init__()
        require_semver(self.schema_contract, field="schema contract")
        _require_string(self.migration_head, "migration_head")
        _require_string(self.migrations_package, "migrations_package")
        ids = [item.id for item in self.objects]
        physical = [item.physical_name for item in self.objects]
        if len(ids) != len(set(ids)):
            raise ManifestError(f"component {self.component_id} declares duplicate object ids")
        if len(physical) != len(set(physical)):
            raise ManifestError(f"component {self.component_id} declares duplicate physical objects")
        dependencies = [item.component for item in self.requires]
        if self.component_id in dependencies:
            raise ManifestError("a component cannot require itself")
        if len(dependencies) != len(set(dependencies)):
            raise ManifestError(f"component {self.component_id} repeats a schema requirement")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "StorageManifest":
        try:
            component = data["component"]
            schema = data["schema"]
            object_rows = schema.get("objects", ())
            requirement_rows = schema.get("requires", ())
            return cls(
                manifest_version=_require_string(data["manifest_version"], "manifest_version"),
                component_id=_require_string(component["id"], "component.id"),
                distribution=_require_string(component["distribution"], "component.distribution"),
                import_root=_require_string(component["import_root"], "component.import_root"),
                schema_contract=_require_string(schema["contract"], "schema.contract"),
                migration_head=_require_string(schema["migration_head"], "schema.migration_head"),
                migrations_package=_require_string(
                    schema["migrations_package"], "schema.migrations_package"
                ),
                objects=tuple(DatabaseObject(**row) for row in object_rows),
                requires=tuple(SchemaRequirement(**row) for row in requirement_rows),
            )
        except (KeyError, TypeError) as exc:
            raise ManifestError(f"invalid storage manifest structure: {exc}") from exc

    @classmethod
    def from_text(cls, text: str) -> "StorageManifest":
        try:
            return cls.from_mapping(tomllib.loads(text))
        except tomllib.TOMLDecodeError as exc:
            raise ManifestError("invalid storage manifest TOML") from exc

    @classmethod
    def from_toml(cls, path: str | Path) -> "StorageManifest":
        return cls.from_text(Path(path).read_text(encoding="utf-8"))

    def canonical_mapping(self) -> dict[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "component": {
                "id": self.component_id,
                "distribution": self.distribution,
                "import_root": self.import_root,
            },
            "schema": {
                "contract": self.schema_contract,
                "migration_head": self.migration_head,
                "migrations_package": self.migrations_package,
                "objects": [
                    {
                        "id": item.id,
                        "kind": item.kind,
                        "physical_name": item.physical_name,
                        **({"model": item.model} if item.model is not None else {}),
                    }
                    for item in sorted(self.objects, key=lambda item: item.id)
                ],
                "requires": [
                    {
                        "component": item.component,
                        "contract": item.contract,
                        "minimum_revision": item.minimum_revision,
                    }
                    for item in sorted(self.requires, key=lambda item: item.component)
                ],
            },
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_mapping(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

    def to_toml(self) -> str:
        """Serialize in a canonical, deterministic order."""
        def quote(value: str) -> str:
            return json.dumps(value, ensure_ascii=True)

        lines = [
            f"manifest_version = {quote(self.manifest_version)}",
            "",
            "[component]",
            f"id = {quote(self.component_id)}",
            f"distribution = {quote(self.distribution)}",
            f"import_root = {quote(self.import_root)}",
            "",
            "[schema]",
            f"contract = {quote(self.schema_contract)}",
            f"migration_head = {quote(self.migration_head)}",
            f"migrations_package = {quote(self.migrations_package)}",
        ]
        for item in sorted(self.objects, key=lambda value: value.id):
            lines.extend(
                [
                    "",
                    "[[schema.objects]]",
                    f"id = {quote(item.id)}",
                    f"kind = {quote(item.kind)}",
                    f"physical_name = {quote(item.physical_name)}",
                ]
            )
            if item.model is not None:
                lines.append(f"model = {quote(item.model)}")
        for requirement in sorted(self.requires, key=lambda value: value.component):
            lines.extend(
                [
                    "",
                    "[[schema.requires]]",
                    f"component = {quote(requirement.component)}",
                    f"contract = {quote(requirement.contract)}",
                    f"minimum_revision = {quote(requirement.minimum_revision)}",
                ]
            )
        return "\n".join(lines) + "\n"


def validate_unique_objects(manifests: Iterable[StorageManifest]) -> None:
    by_id: dict[str, str] = {}
    by_physical: dict[str, str] = {}
    for manifest in manifests:
        for item in manifest.objects:
            prior_id = by_id.setdefault(item.id, manifest.component_id)
            if prior_id != manifest.component_id:
                raise ManifestError(
                    f"database object id {item.id} is claimed by {prior_id} and {manifest.component_id}"
                )
            prior_physical = by_physical.setdefault(item.physical_name, manifest.component_id)
            if prior_physical != manifest.component_id:
                raise ManifestError(
                    f"database object {item.physical_name} is claimed by "
                    f"{prior_physical} and {manifest.component_id}"
                )
