from tigrbl_base._base._binding_base import BindingBase, BindingRegistryBase
from tigrbl_core._spec.binding_spec import BindingRegistrySpec, BindingSpec, HTTPBindingSpec


def test_binding_base_inheritance() -> None:
    assert issubclass(BindingBase, BindingSpec)
    assert issubclass(BindingRegistryBase, BindingRegistrySpec)


def test_binding_registry_base_registers_and_replaces_by_name() -> None:
    first = BindingBase(name="rest", spec=HTTPBindingSpec(path="/items"))
    second = BindingBase(name="rest", spec=HTTPBindingSpec(path="/users"))
    registry = BindingRegistryBase()

    registry.register(first)
    registry.register(second)

    assert registry.get("rest") is second
    assert registry.values() == (second,)


def test_binding_registry_base_preserves_insertion_order() -> None:
    rest = BindingBase(name="rest", spec=HTTPBindingSpec(path="/items"))
    admin = BindingBase(name="admin", spec=HTTPBindingSpec(path="/admin"))
    registry = BindingRegistryBase()

    registry.register(rest)
    registry.register(admin)

    assert registry.values() == (rest, admin)
    assert registry.get("missing") is None
