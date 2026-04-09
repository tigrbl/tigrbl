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
