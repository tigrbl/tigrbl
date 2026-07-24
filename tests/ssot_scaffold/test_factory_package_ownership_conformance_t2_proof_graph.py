import pytest

from tigrbl_tests.factory_conformance import FactorySurface, assert_owner


def test_facade_owned_concrete_factory_is_rejected():
    surface = FactorySurface(
        path="tigrbl.factories.column:makeColumn",
        owner="concrete",
        verb="make",
        form="function",
        descriptor="function",
        async_mode="sync",
        returns="descriptor-instance",
        side_effects="construction",
        stability="stable",
    )
    with pytest.raises(AssertionError, match="wrong prefix"):
        assert_owner(surface)
