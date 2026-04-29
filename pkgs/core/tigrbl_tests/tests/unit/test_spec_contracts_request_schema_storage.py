from __future__ import annotations

from tigrbl import SchemaRef, SchemaSpec, StorageTypeRef
from tigrbl_core._spec import RequestSpec, StorageTransformSpec
from tigrbl_core._spec.datatypes import (
    DataTypeSpec,
    EngineDatatypeBridge,
    ReflectedTypeMapper,
)


def _strip_for_storage(value: object, _ctx: object) -> object:
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _identity_from_storage(value: object, _ctx: object) -> object:
    return value


def test_requestspec_preserves_explicit_request_shape_and_bytes_serde() -> None:
    spec = RequestSpec(
        method="POST",
        path="/items/42",
        headers={"content-type": "application/json"},
        query={"include": ["owner", "audit"]},
        path_params={"id": "42"},
        body=b'{"name":"Ada"}',
        script_name="/api",
    )

    restored = RequestSpec.from_json(spec.to_json())

    assert restored.method == "POST"
    assert restored.path == "/items/42"
    assert restored.headers["content-type"] == "application/json"
    assert restored.query["include"] == ["owner", "audit"]
    assert restored.path_params["id"] == "42"
    assert restored.body == b'{"name":"Ada"}'
    assert restored.script_name == "/api"


def test_schemaref_is_lazy_alias_and_direction_metadata() -> None:
    ref = SchemaRef("Search", "out")

    assert ref.alias == "Search"
    assert ref.kind == "out"


def test_schemaspec_roundtrips_schema_refs_and_inline_schema_payloads() -> None:
    ref_spec = SchemaSpec(alias="search.response", kind="out", schema=SchemaRef("Search", "out"))
    inline_spec = SchemaSpec(
        alias="search.request",
        kind="in",
        schema={
            "type": "object",
            "required": ["q"],
            "properties": {"q": {"type": "string"}},
        },
    )

    restored_ref = SchemaSpec.from_dict(ref_spec.to_dict())
    restored_inline = SchemaSpec.from_json(inline_spec.to_json())

    assert restored_ref.schema == SchemaRef("Search", "out")
    assert restored_inline.schema["required"] == ["q"]
    assert restored_inline.schema["properties"]["q"]["type"] == "string"


def test_storagetransformspec_roundtrips_named_transform_callables() -> None:
    transform = StorageTransformSpec(
        to_stored=_strip_for_storage,
        from_stored=_identity_from_storage,
    )

    restored = StorageTransformSpec.from_dict(transform.to_dict())

    assert restored.to_stored(" ADA@EXAMPLE.COM ", {}) == "ada@example.com"
    assert restored.from_stored("stored", {}) == "stored"


def test_storagetyperef_lowers_and_reflects_engine_physical_types() -> None:
    bridge = EngineDatatypeBridge()

    postgres_type = bridge.lower("postgres", DataTypeSpec("json"))
    sqlite_type = bridge.lower("sqlite", DataTypeSpec("string"))

    assert postgres_type == StorageTypeRef(engine_kind="postgres", physical_name="JSONB")
    assert sqlite_type == StorageTypeRef(engine_kind="sqlite", physical_name="TEXT")

    mapper = ReflectedTypeMapper()
    logical = mapper.from_storage_ref(postgres_type)

    assert logical.logical_name == "json"


def test_storagetyperef_is_public_and_json_serializable() -> None:
    ref = StorageTypeRef(engine_kind="sqlite", physical_name="TEXT")

    restored = StorageTypeRef.from_json(ref.to_json())

    assert restored == ref
