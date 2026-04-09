from __future__ import annotations

from tigrbl_core._spec import BaseTypeAdapter, DataTypeSpec, TypeRegistry


class StringAdapter(BaseTypeAdapter):
    logical_name = "string"


def test_adapter_registry_contract_registers_and_normalizes_known_type() -> None:
    registry = TypeRegistry()
    registry.register(StringAdapter())

    normalized = registry.normalize(
        DataTypeSpec(logical_name="string"),
        factories={"string": StringAdapter},
    )

    assert normalized.logical_name == "string"
    assert registry.registered_names() == ("string",)
