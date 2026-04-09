from __future__ import annotations

from tigrbl_core._spec import BaseTypeAdapter, DataTypeSpec, TypeRegistry


class StringAdapter(BaseTypeAdapter):
    logical_name = "string"


def test_adapter_registry_contract_registers_and_normalizes_known_type() -> None:
    registry = TypeRegistry(include_builtins=False)
    registry.register(StringAdapter())

    normalized = registry.normalize(
        DataTypeSpec(logical_name="string"),
    )

    assert normalized.logical_name == "string"
    assert registry.registered_names() == ("string",)


def test_adapter_registry_contract_round_trips_registered_adapter_paths() -> None:
    registry = TypeRegistry(include_builtins=False)
    registry.register(StringAdapter())

    restored = TypeRegistry.from_json(registry.to_json())

    assert restored.registered_names() == ("string",)
    resolved = restored.resolve("string")
    assert resolved is not None
    assert resolved.normalize(DataTypeSpec(logical_name="string")).logical_name == "string"
