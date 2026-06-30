from __future__ import annotations

from tigrbl_core._spec import BaseTypeAdapter, DataTypeSpec, TypeAdapter, TypeRegistry


class StringAdapter(BaseTypeAdapter):
    logical_name = "string"


class UpperStringAdapter(BaseTypeAdapter):
    logical_name = "String"

    def encode(self, value):
        return str(value).upper()

    def decode(self, value):
        return str(value).lower()

    def to_json(self, value):
        return {"value": self.encode(value)}

    def to_df(self, value):
        return self.decode(value)


def test_adapter_protocol_exposes_required_methods() -> None:
    adapter = UpperStringAdapter()

    assert isinstance(adapter, TypeAdapter)
    for method_name in ("normalize", "encode", "decode", "to_json", "to_df"):
        assert callable(getattr(adapter, method_name))


def test_adapter_registry_contract_registers_and_normalizes_known_type() -> None:
    registry = TypeRegistry(include_builtins=False)
    registry.register(StringAdapter())

    normalized = registry.normalize(
        DataTypeSpec(logical_name="string"),
    )

    assert normalized.logical_name == "string"
    assert registry.registered_names() == ("string",)


def test_adapter_registry_normalizes_logical_names_on_register() -> None:
    registry = TypeRegistry(include_builtins=False)
    registry.register(UpperStringAdapter())

    assert registry.registered_names() == ("string",)
    assert registry.resolve(" String ") is not None
    assert registry.resolve("text") is not None


def test_adapter_registry_contract_round_trips_registered_adapter_paths() -> None:
    registry = TypeRegistry(include_builtins=False)
    registry.register(StringAdapter())

    restored = TypeRegistry.from_json(registry.to_json())

    assert restored.registered_names() == ("string",)
    resolved = restored.resolve("string")
    assert resolved is not None
    assert resolved.normalize(DataTypeSpec(logical_name="string")).logical_name == "string"


def test_adapter_registry_encode_decode_delegates_to_registered_adapter() -> None:
    registry = TypeRegistry(include_builtins=False)
    registry.register(UpperStringAdapter())

    assert registry.encode("string", "ada") == "ADA"
    assert registry.decode("text", "ADA") == "ada"
    assert registry.resolve("string").to_json("ada") == {"value": "ADA"}
    assert registry.resolve("string").to_df("ADA") == "ada"


def test_adapter_registry_unknown_type_falls_back_deterministically() -> None:
    registry = TypeRegistry(include_builtins=False)
    spec = DataTypeSpec(logical_name="custom", nullable=True, options={"x": 1})

    assert registry.resolve("custom") is None
    assert registry.normalize(spec) == spec
    assert registry.encode("custom", {"raw": True}) == {"raw": True}
    assert registry.decode("custom", {"raw": True}) == {"raw": True}
