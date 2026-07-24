from tigrbl_tests.factory_conformance import discover_factory_candidates


def test_ast_discovery_finds_standalone_class_async_camelcase_and_alias(tmp_path):
    source = tmp_path / "surfaces.py"
    source.write_text(
        "def make_item(): pass\n"
        "async def deriveAsync(): pass\n"
        "class Builder:\n"
        "    @classmethod\n"
        "    def define(cls): pass\n"
        "provide = make_item\n",
        encoding="utf-8",
    )
    candidates = discover_factory_candidates((source,))
    found = {(item.qualname, item.form, item.async_mode) for item in candidates}
    assert ("make_item", "function", "sync") in found
    assert ("deriveAsync", "function", "async") in found
    assert ("Builder.define", "classmethod", "sync") in found
    assert ("provide", "alias", "unknown") in found
