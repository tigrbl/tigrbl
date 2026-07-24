import sys
from types import ModuleType

import pytest

from tigrbl_tests.factory_conformance import FactoryAlias, FactorySurface
from tigrbl_tests.factory_conformance.aliases import assert_alias_parity


def test_aggregate_conformance_rejects_behavioral_alias_drift():
    module = ModuleType("factory_bad_aggregate")

    def canonical(*, value: int = 1) -> int:
        return value

    def alias(*, changed: str = "bad") -> str:
        return changed

    module.canonical = canonical
    module.alias = alias
    sys.modules[module.__name__] = module
    surface = FactorySurface(
        path="factory_bad_aggregate:canonical",
        owner="concrete",
        verb="make",
        form="function",
        descriptor="function",
        async_mode="sync",
        returns="value",
        side_effects="construction",
        stability="stable",
    )
    with pytest.raises(AssertionError, match="identity|signature"):
        assert_alias_parity(
            surface,
            FactoryAlias(path="factory_bad_aggregate:alias", form="identity"),
        )
