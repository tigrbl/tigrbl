from __future__ import annotations

from importlib import resources

from tigrbl_spec import CURRENT_SCHEMA_VERSION, load_bundle, load_manifest, load_schema, spec_kinds


def test_schema_catalog_package_contains_manifest_bundle_shared_and_specs() -> None:
    root = resources.files("tigrbl_spec").joinpath("schemas", CURRENT_SCHEMA_VERSION)

    assert root.joinpath("manifest.json").is_file()
    assert root.joinpath("bundle.json").is_file()
    assert root.joinpath("shared.json").is_file()
    assert root.joinpath("AppSpec.json").is_file()


def test_package_can_load_current_schema_manifest_and_bundle() -> None:
    manifest = load_manifest()
    bundle = load_bundle()

    assert manifest["catalog_version"] == CURRENT_SCHEMA_VERSION
    assert manifest["authority"] == "tigrbl_spec"
    assert manifest["schemas"]["AppSpec"] == "AppSpec.json"
    assert manifest["schemas"]["HeadersSpec"] == "HeadersSpec.json"
    assert bundle["catalog_version"] == CURRENT_SCHEMA_VERSION
    assert bundle["schemas"]["ColumnSpec"] == "#/$defs/ColumnSpec"
    assert bundle["schemas"]["HeadersSpec"] == "#/$defs/HeadersSpec"
    assert "AppSpec" in spec_kinds()
    assert "HeadersSpec" in spec_kinds()


def test_loaded_schema_contains_identity_fields() -> None:
    schema = load_schema("AppSpec")

    assert schema["properties"]["spec_kind"]["const"] == "AppSpec"
    assert schema["properties"]["spec_schema_version"]["const"] == CURRENT_SCHEMA_VERSION
    assert schema["properties"]["spec_type"]["const"] == (
        f"urn:tigrbl:spec:AppSpec:{CURRENT_SCHEMA_VERSION}"
    )


def test_headers_schema_contains_identity_and_collection_fields() -> None:
    schema = load_schema("HeadersSpec")

    assert schema["properties"]["spec_kind"]["const"] == "HeadersSpec"
    assert schema["properties"]["spec_schema_version"]["const"] == CURRENT_SCHEMA_VERSION
    assert schema["properties"]["spec_type"]["const"] == (
        f"urn:tigrbl:spec:HeadersSpec:{CURRENT_SCHEMA_VERSION}"
    )
    assert schema["properties"]["values"] == {"$ref": "./shared.json#/$defs/StringMap"}
    assert schema["properties"]["required"] == {"$ref": "./shared.json#/$defs/StringTuple"}
    assert schema["properties"]["expose"] == {"$ref": "./shared.json#/$defs/StringTuple"}
