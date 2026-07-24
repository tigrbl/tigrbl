from tigrbl_tests.factory_conformance import load_manifest


def test_registered_verbs_declare_structural_semantics():
    for surface in load_manifest().surfaces:
        assert surface.verb in {"define", "derive", "make", "provide"}
        assert surface.async_mode in {"sync", "async"}
        if surface.verb == "define":
            assert surface.side_effects == "none"
