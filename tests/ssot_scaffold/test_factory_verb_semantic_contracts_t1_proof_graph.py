from tigrbl_concrete.factories.app import defineAppSpec, deriveApp
from tigrbl_concrete.factories.column import makeColumn
from tigrbl_core._spec.app_spec import AppSpec


def test_define_derive_and_make_have_distinct_outputs():
    spec = defineAppSpec(title="Factory contract")
    app_type = deriveApp(title="Factory contract")
    column = makeColumn()
    assert issubclass(spec, AppSpec)
    assert app_type is not spec
    assert column.__class__.__name__ == "Column"
