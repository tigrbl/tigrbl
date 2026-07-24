from tigrbl_tests.factory_conformance import assert_alias_parity, load_manifest


def test_all_direct_aliases_and_reexports_preserve_parity():
    for surface in load_manifest().surfaces:
        for alias in surface.aliases:
            assert_alias_parity(surface, alias)
