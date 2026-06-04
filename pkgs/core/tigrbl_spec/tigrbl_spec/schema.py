from __future__ import annotations

import copy
import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, exceptions
from referencing import Registry, Resource

CURRENT_SCHEMA_VERSION = "0.3.20"
SCHEMA_VERSION = CURRENT_SCHEMA_VERSION
SPEC_TYPE_PREFIX = "urn:tigrbl:spec"


class SpecSchemaError(ValueError):
    """Base error for tigrbl_spec schema catalog failures."""


class UnknownSpecKindError(SpecSchemaError):
    """Raised when a payload references an unknown spec kind."""


class UnsupportedSchemaVersionError(SpecSchemaError):
    """Raised when a catalog version is not packaged or supported."""


class SpecValidationError(SpecSchemaError):
    """Raised when a spec payload does not satisfy its schema."""


def spec_type(spec_kind: str, version: str = CURRENT_SCHEMA_VERSION) -> str:
    return f"{SPEC_TYPE_PREFIX}:{spec_kind}:{version}"


def identity_fields(spec_kind: str, version: str = CURRENT_SCHEMA_VERSION) -> dict[str, str]:
    return {
        "spec_kind": spec_kind,
        "spec_schema_version": version,
        "spec_type": spec_type(spec_kind, version),
    }


def schemas_root() -> resources.abc.Traversable:
    return resources.files("tigrbl_spec").joinpath("schemas")


def schema_versions() -> tuple[str, ...]:
    versions = [
        item.name
        for item in schemas_root().iterdir()
        if item.is_dir() and item.joinpath("manifest.json").is_file()
    ]
    return tuple(sorted(versions))


def _require_version(version: str) -> None:
    if version not in schema_versions():
        raise UnsupportedSchemaVersionError(
            f"Unsupported tigrbl_spec schema catalog version {version!r}; "
            f"available versions: {', '.join(schema_versions()) or '<none>'}"
        )


@lru_cache(maxsize=None)
def _load_json_file(version: str, filename: str) -> dict[str, Any]:
    _require_version(version)
    path = schemas_root().joinpath(version, filename)
    if not path.is_file():
        raise FileNotFoundError(f"Schema catalog file not found: {version}/{filename}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_manifest(version: str = CURRENT_SCHEMA_VERSION) -> dict[str, Any]:
    return copy.deepcopy(_load_json_file(version, "manifest.json"))


def load_bundle(version: str = CURRENT_SCHEMA_VERSION) -> dict[str, Any]:
    return copy.deepcopy(_load_json_file(version, "bundle.json"))


def spec_kinds(version: str = CURRENT_SCHEMA_VERSION) -> tuple[str, ...]:
    manifest = load_manifest(version)
    return tuple(sorted((manifest.get("schemas") or {}).keys()))


def schema_path(spec_kind: str, version: str = CURRENT_SCHEMA_VERSION) -> Path:
    if spec_kind not in spec_kinds(version):
        raise UnknownSpecKindError(f"Unknown tigrbl_spec kind {spec_kind!r}")
    return Path(str(schemas_root().joinpath(version, f"{spec_kind}.json")))


def load_schema(spec_kind: str, version: str = CURRENT_SCHEMA_VERSION) -> dict[str, Any]:
    if spec_kind not in spec_kinds(version):
        raise UnknownSpecKindError(f"Unknown tigrbl_spec kind {spec_kind!r}")
    return copy.deepcopy(_load_json_file(version, f"{spec_kind}.json"))


def with_identity(
    spec_kind: str,
    payload: dict[str, Any],
    version: str = CURRENT_SCHEMA_VERSION,
) -> dict[str, Any]:
    identified = dict(payload)
    identified.update(identity_fields(spec_kind, version))
    return identified


def _identity_version(payload: dict[str, Any]) -> str:
    value = payload.get("spec_schema_version")
    if not isinstance(value, str):
        raise SpecValidationError("Spec payload must include string spec_schema_version")
    return value


def _validate_identity(spec_kind: str, payload: dict[str, Any], version: str) -> None:
    expected = identity_fields(spec_kind, version)
    for field, expected_value in expected.items():
        actual = payload.get(field)
        if actual != expected_value:
            raise SpecValidationError(
                f"Spec payload identity field {field!r} must be {expected_value!r}; got {actual!r}"
            )


@lru_cache(maxsize=None)
def _registry(version: str) -> Registry:
    _require_version(version)
    base_uri = f"urn:tigrbl:spec:schema-catalog:{version}/"
    pairs = []
    manifest = load_manifest(version)
    filenames = ["shared.json", *(manifest.get("schemas") or {}).values()]
    for filename in filenames:
        schema = _load_json_file(version, filename)
        pairs.append((base_uri + filename, Resource.from_contents(schema)))
    return Registry().with_resources(pairs)


@lru_cache(maxsize=None)
def _validator(spec_kind: str, version: str) -> Draft202012Validator:
    schema = load_schema(spec_kind, version)
    base_uri = f"urn:tigrbl:spec:schema-catalog:{version}/"
    return Draft202012Validator(schema, registry=_registry(version), _resolver=None).evolve(
        schema={**schema, "$id": base_uri + f"{spec_kind}.json"}
    )


def validate_payload(
    spec_kind: str,
    payload: dict[str, Any],
    version: str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SpecValidationError("Spec payload must be a JSON object")
    resolved_version = version or _identity_version(payload)
    _require_version(resolved_version)
    if spec_kind not in spec_kinds(resolved_version):
        raise UnknownSpecKindError(f"Unknown tigrbl_spec kind {spec_kind!r}")
    _validate_identity(spec_kind, payload, resolved_version)
    try:
        _validator(spec_kind, resolved_version).validate(payload)
    except exceptions.ValidationError as exc:
        location = ".".join(str(part) for part in exc.absolute_path)
        prefix = f"{spec_kind} payload"
        if location:
            prefix = f"{prefix} at {location}"
        raise SpecValidationError(f"{prefix} failed schema validation: {exc.message}") from exc
    return copy.deepcopy(payload)


def load_payload(
    spec_kind: str,
    payload: dict[str, Any],
    *,
    migrate: bool = False,
    to_version: str = CURRENT_SCHEMA_VERSION,
) -> dict[str, Any]:
    from tigrbl_spec.migrations import migrate_payload

    version = _identity_version(payload)
    loaded = migrate_payload(spec_kind, payload, version, to_version) if migrate else payload
    return validate_payload(spec_kind, loaded, to_version if migrate else version)


INDIVIDUAL_SPEC_NAMES = spec_kinds(CURRENT_SCHEMA_VERSION)
JSON_SCHEMA_DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"
SHARED_SCHEMA_NAME = "shared.json"


def build_shared_json_schema() -> dict[str, Any]:
    return _load_json_file(CURRENT_SCHEMA_VERSION, SHARED_SCHEMA_NAME)


def build_individual_spec_json_schemas() -> dict[str, dict[str, Any]]:
    return {kind: load_schema(kind) for kind in INDIVIDUAL_SPEC_NAMES}


def build_spec_json_schema_bundle() -> dict[str, Any]:
    return load_manifest()
