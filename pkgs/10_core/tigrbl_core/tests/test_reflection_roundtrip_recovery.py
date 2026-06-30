from __future__ import annotations

import pytest

from tigrbl_core._spec import ReflectedTypeMapper, StorageTypeRef


def test_reflected_mapper_maps_postgres_jsonb_to_json() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.from_storage_ref(
        StorageTypeRef(engine_kind="postgres", physical_name="JSONB"),
    )

    assert recovered.logical_name == "json"
    assert recovered.options == {}


def test_reflected_mapper_maps_sqlite_text_to_string() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.from_storage_ref(
        StorageTypeRef(engine_kind="sqlite", physical_name="TEXT"),
    )

    assert recovered.logical_name == "string"


def test_reflection_roundtrip_recovery_preserves_metadata_in_metadata_mode() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.from_storage_ref(
        StorageTypeRef(engine_kind="postgres", physical_name="JSONB"),
        mode="metadata_preserving",
    )
    assert recovered.logical_name == "json"
    assert recovered.options["reflected_physical_name"] == "JSONB"
    assert recovered.options["reflected_engine_kind"] == "postgres"


def test_reflected_mapper_matches_physical_names_case_insensitively() -> None:
    mapper = ReflectedTypeMapper()

    upper = mapper.from_storage_ref(StorageTypeRef(engine_kind="postgres", physical_name="JSONB"))
    lower = mapper.from_storage_ref(StorageTypeRef(engine_kind="postgres", physical_name="jsonb"))

    assert upper.logical_name == lower.logical_name == "json"


def test_reflection_roundtrip_recovery_can_fail_closed_when_unknown() -> None:
    mapper = ReflectedTypeMapper()
    with pytest.raises(LookupError):
        mapper.from_storage_ref(
            StorageTypeRef(engine_kind="postgres", physical_name="UNSUPPORTED"),
            strict=True,
        )


def test_reflected_mapper_logical_hint_overrides_physical_inference() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.reflect(
        engine_kind="postgres",
        physical_name="JSONB",
        logical_hint="string",
        mode="metadata_preserving",
    )

    assert recovered.logical_name == "string"
    assert recovered.options["reflected_physical_name"] == "JSONB"
    assert recovered.options["reflected_engine_kind"] == "postgres"
