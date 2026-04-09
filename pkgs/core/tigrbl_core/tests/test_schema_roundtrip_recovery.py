from __future__ import annotations

from tigrbl_core._spec import ReflectedTypeMapper


def test_schema_roundtrip_recovery_accepts_logical_hint_override() -> None:
    mapper = ReflectedTypeMapper()
    recovered = mapper.reflect(
        engine_kind="sqlite",
        physical_name="TEXT",
        logical_hint="string",
        mode="best_effort",
    )
    assert recovered.logical_name == "string"
