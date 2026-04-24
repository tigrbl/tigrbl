from __future__ import annotations

from tigrbl_core.schema import (
    INDIVIDUAL_SPEC_NAMES,
    JSON_SCHEMA_DRAFT_2020_12,
    SHARED_SCHEMA_NAME,
    build_individual_spec_json_schemas,
    build_shared_json_schema,
    build_spec_json_schema_bundle,
)


def test_spec_json_schema_bundle_is_manifest_for_shared_and_individual_files() -> None:
    bundle = build_spec_json_schema_bundle()

    assert bundle["$schema"] == JSON_SCHEMA_DRAFT_2020_12
    assert bundle["title"] == "Tigrbl Core Spec Schema Manifest"
    assert bundle["shared"] == SHARED_SCHEMA_NAME
    assert bundle["schemas"]["AppSpec"] == "AppSpec.json"
    assert bundle["schemas"]["ColumnSpec"] == "ColumnSpec.json"


def test_shared_schema_contains_common_defs_and_transport_union() -> None:
    shared_schema = build_shared_json_schema()
    defs = shared_schema["$defs"]

    assert shared_schema["$schema"] == JSON_SCHEMA_DRAFT_2020_12
    assert shared_schema["$id"] == SHARED_SCHEMA_NAME
    assert "SerdeValue" in defs
    assert "TransportBindingSpec" in defs
    assert defs["TransportBindingSpec"]["anyOf"][0] == {"$ref": "./HttpRestBindingSpec.json"}


def test_datatype_schema_tracks_canonical_logical_names() -> None:
    datatype_schema = build_individual_spec_json_schemas()["DataTypeSpec"]
    logical_name = datatype_schema["properties"]["logical_name"]

    assert logical_name["type"] == "string"
    assert "uuid" in logical_name["enum"]
    assert "json" in logical_name["enum"]
    assert "ulid" in logical_name["enum"]


def test_binding_and_column_specs_reference_nested_spec_shapes() -> None:
    schemas = build_individual_spec_json_schemas()
    binding_spec = schemas["BindingSpec"]
    column_spec = schemas["ColumnSpec"]

    assert binding_spec["properties"]["spec"] == {"$ref": "./shared.json#/$defs/TransportBindingSpec"}
    storage_any_of = column_spec["properties"]["storage"]["anyOf"][0]["anyOf"]
    assert storage_any_of[0] == {"$ref": "./StorageSpec.json"}
    assert storage_any_of[1] == {
        "$ref": "./StorageSpec.json#/$defs/StorageSpecEnvelope"
    }
    assert schemas["ColumnSpec"]["$defs"]["ColumnSpecEnvelope"]["properties"]["__dataclass__"]["const"] == (
        "tigrbl_core._spec.column_spec:ColumnSpec"
    )


def test_individual_schemas_are_emitted_per_spec() -> None:
    schemas = build_individual_spec_json_schemas()

    assert set(INDIVIDUAL_SPEC_NAMES).issubset(schemas)
    assert schemas["AppSpec"]["$id"] == "AppSpec.json"
    assert schemas["ColumnSpec"]["$id"] == "ColumnSpec.json"
    assert schemas["OpSpec"]["$id"] == "OpSpec.json"
    assert schemas["WsBindingSpec"]["$id"] == "WsBindingSpec.json"
