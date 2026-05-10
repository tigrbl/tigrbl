from tigrbl_concrete._concrete._engine import provider_from_spec
from tigrbl_core._spec.engine_spec import EngineProviderSpec, EngineSpec


def test_concrete_engine_lowering_contract() -> None:
    spec = EngineSpec.from_any({"kind": "sqlite", "memory": True, "name": "primary"})
    provider = provider_from_spec(spec)

    assert isinstance(provider.spec, EngineSpec)
    assert EngineProviderSpec.from_any(provider).spec.kind == "sqlite"
