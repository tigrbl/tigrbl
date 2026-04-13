from __future__ import annotations

import pytest

from tigrbl_core._spec import ReflectedTypeMapper, StorageTypeRef


def test_reflection_roundtrip_recovery_preserves_metadata_in_metadata_mode() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.from_storage_ref(
        StorageTypeRef(engine_kind="postgres", physical_name="JSONB"),
        mode="metadata_preserving",
    )
    assert recovered.logical_name == "json"
    assert recovered.options["reflected_physical_name"] == "JSONB"
    assert recovered.options["reflected_engine_kind"] == "postgres"


def test_reflection_roundtrip_recovery_can_fail_closed_when_unknown() -> None:
    mapper = ReflectedTypeMapper()
    with pytest.raises(LookupError):
        mapper.from_storage_ref(
            StorageTypeRef(engine_kind="postgres", physical_name="UNSUPPORTED"),
            strict=True,
        )
