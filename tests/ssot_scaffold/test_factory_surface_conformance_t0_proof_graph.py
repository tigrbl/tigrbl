from tigrbl_tests.factory_conformance import load_manifest


def test_factory_manifest_has_complete_baseline():
    manifest = load_manifest()
    assert manifest.version == 1
    assert len(manifest.surfaces) >= 13
    for surface in manifest.surfaces:
        assert surface.path
        assert surface.owner
        assert surface.returns
        assert surface.side_effects
        assert surface.stability
