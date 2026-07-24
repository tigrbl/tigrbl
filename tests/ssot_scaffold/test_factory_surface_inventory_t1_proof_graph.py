from tigrbl_tests.factory_conformance import load_manifest, resolve_symbol


def test_every_manifest_symbol_and_alias_resolves():
    for surface in load_manifest().surfaces:
        assert resolve_symbol(surface.path) is not None
        for alias in surface.aliases:
            assert resolve_symbol(alias.path) is not None
