from __future__ import annotations

from tigrbl_core._spec.table_spec import TableSpec


def test_table_portability_contract_exposes_portability_metadata() -> None:
    spec = TableSpec(
        model_ref="pkg.models:Widget",
        portability_class="relational-portable",
        interoperable_with=("sqlite", "postgres"),
        roundtrip_mode="metadata_preserving",
    )
    assert spec.portability_class == "relational-portable"
    assert tuple(spec.interoperable_with) == ("sqlite", "postgres")
    assert spec.roundtrip_mode == "metadata_preserving"


def test_table_portability_contract_collects_metadata_from_table_config() -> None:
    class Demo:
        table_config = {
            "portability_class": "cache-portable",
            "interoperable_with": ("redis", "memory"),
            "roundtrip_mode": "best_effort",
        }

    spec = TableSpec.collect(Demo)

    assert spec.portability_class == "cache-portable"
    assert tuple(spec.interoperable_with) == ("redis", "memory")
    assert spec.roundtrip_mode == "best_effort"
