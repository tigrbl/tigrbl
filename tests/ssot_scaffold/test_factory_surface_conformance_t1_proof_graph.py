from tigrbl_tests.factory_conformance import (
    assert_alias_parity,
    assert_owner,
    assert_surface_shape,
    load_manifest,
)


def test_all_registered_factory_surfaces_conform():
    for surface in load_manifest().surfaces:
        assert_owner(surface)
        assert_surface_shape(surface)
        for alias in surface.aliases:
            assert_alias_parity(surface, alias)
