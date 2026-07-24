import sys
from types import ModuleType

import pytest

from tigrbl_tests.factory_conformance import FactoryAlias, FactorySurface
from tigrbl_tests.factory_conformance.aliases import assert_alias_parity


def test_identity_alias_cannot_silently_become_a_wrapper():
    module = ModuleType("factory_bad_alias")

    def canonical(value=1):
        return value

    def wrapper(value=1):
        return canonical(value)

    module.canonical = canonical
    module.wrapper = wrapper
    sys.modules[module.__name__] = module
    surface = FactorySurface(
        path="factory_bad_alias:canonical",
        owner="concrete",
        verb="make",
        form="function",
        descriptor="function",
        async_mode="sync",
        returns="value",
        side_effects="construction",
        stability="stable",
    )
    with pytest.raises(AssertionError, match="preserve identity"):
        assert_alias_parity(
            surface,
            FactoryAlias(path="factory_bad_alias:wrapper", form="identity"),
        )
