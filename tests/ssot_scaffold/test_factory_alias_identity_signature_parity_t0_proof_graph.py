from tigrbl_tests.factory_conformance import load_manifest


def test_aliases_have_explicit_forms_and_lifecycle():
    aliases = [alias for surface in load_manifest().surfaces for alias in surface.aliases]
    assert aliases
    assert {alias.form for alias in aliases} <= {"identity", "re-export", "wrapper"}
    assert all(alias.stability in {"stable", "deprecated", "experimental"} for alias in aliases)
