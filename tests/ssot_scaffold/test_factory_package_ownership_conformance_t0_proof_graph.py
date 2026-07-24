from tigrbl_tests.factory_conformance import assert_owner, load_manifest


def test_manifest_package_placements_match_declared_owners():
    for surface in load_manifest().surfaces:
        assert_owner(surface)
