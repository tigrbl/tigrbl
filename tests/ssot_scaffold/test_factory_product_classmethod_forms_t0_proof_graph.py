from tigrbl_tests.factory_conformance import load_manifest


def test_factory_product_classmethods_are_manifested():
    surfaces = load_manifest().by_path()
    expected = {
        "tigrbl_concrete._concrete._column:Column.make",
        "tigrbl_concrete._concrete._op:Op.make",
        "tigrbl_concrete._concrete.tigrbl_app:TigrblApp.define",
        "tigrbl_concrete._concrete.tigrbl_app:TigrblApp.derive",
        "tigrbl_concrete._concrete._router:Router.define",
        "tigrbl_concrete._concrete._router:Router.derive",
        "tigrbl_concrete._concrete._table:Table.define",
        "tigrbl_concrete._concrete._table:Table.derive",
        "tigrbl_concrete._concrete._table:Table.provide",
        "tigrbl_concrete._concrete._table:Table.activate",
    }
    assert expected <= surfaces.keys()
    assert all(surfaces[path].form == "classmethod" for path in expected)
