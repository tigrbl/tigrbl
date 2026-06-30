from __future__ import annotations

import pytest

from tigrbl_core._spec import DataTypeSpec, EngineDatatypeBridge, ReflectedTypeMapper


def test_schema_roundtrip_best_effort_recovers_known_type_without_metadata() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.reflect(
        engine_kind="sqlite",
        physical_name="TEXT",
        mode="best_effort",
    )

    assert recovered.logical_name == "string"
    assert recovered.options == {}


def test_schema_roundtrip_recovery_accepts_logical_hint_override() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.reflect(
        engine_kind="sqlite",
        physical_name="TEXT",
        logical_hint="string",
        mode="best_effort",
    )
    assert recovered.logical_name == "string"


def test_schema_roundtrip_metadata_preserving_mode_records_source() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.reflect(
        engine_kind="postgres",
        physical_name="JSONB",
        mode="metadata_preserving",
    )

    assert recovered.logical_name == "json"
    assert recovered.options["reflected_engine_kind"] == "postgres"
    assert recovered.options["reflected_physical_name"] == "JSONB"


def test_schema_roundtrip_recovery_downgrades_unknown_types_deterministically() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.reflect(
        engine_kind="sqlite",
        physical_name="SOMETHING_NEW",
        mode="metadata_preserving",
    )
    assert recovered.logical_name == "object"
    assert recovered.options["downgraded_from_physical_name"] == "SOMETHING_NEW"


def test_schema_roundtrip_strict_unknown_type_raises() -> None:
    mapper = ReflectedTypeMapper()

    with pytest.raises(LookupError):
        mapper.reflect(
            engine_kind="sqlite",
            physical_name="SOMETHING_NEW",
            strict=True,
        )


@pytest.mark.parametrize(
    ("engine_kind", "logical_name", "expected_physical"),
    (
        ("sqlite", "string", "TEXT"),
        ("sqlite", "json", "JSON"),
        ("postgres", "json", "JSONB"),
        ("postgres", "uuid", "UUID"),
    ),
)
def test_schema_roundtrip_lower_then_reflect_recovers_logical_type(
    engine_kind: str,
    logical_name: str,
    expected_physical: str,
) -> None:
    bridge = EngineDatatypeBridge()
    mapper = ReflectedTypeMapper()

    lowered = bridge.lower(engine_kind, DataTypeSpec(logical_name=logical_name), strict=True)
    recovered = mapper.from_storage_ref(lowered)

    assert lowered.physical_name == expected_physical
    assert recovered.logical_name == logical_name
