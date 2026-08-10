from tigrbl_tests.factory_conformance import assert_surface_shape, load_manifest


def test_factory_product_classmethods_delegate_to_canonical_functions():
    classmethods = [
        surface for surface in load_manifest().surfaces if surface.form == "classmethod"
    ]
    assert classmethods
    for surface in classmethods:
        assert surface.canonical
        assert_surface_shape(surface)
