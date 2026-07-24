import pytest

from tigrbl_tests.factory_conformance import FactorySurface, assert_surface_shape


def test_define_with_declared_initialization_is_rejected():
    surface = FactorySurface(
        path="tigrbl_concrete.factories.app:defineAppSpec",
        owner="concrete",
        verb="define",
        form="function",
        descriptor="function",
        async_mode="sync",
        returns="spec-class",
        side_effects="initialization",
        stability="stable",
    )
    with pytest.raises(AssertionError, match="declarative"):
        assert_surface_shape(surface)
