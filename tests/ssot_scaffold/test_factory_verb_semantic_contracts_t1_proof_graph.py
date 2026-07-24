from tigrbl_concrete.factories.app import defineAppSpec, deriveApp
from tigrbl_concrete.factories.column import makeColumn
from tigrbl_concrete.factories.op import makeOp
from tigrbl_core._spec.app_spec import AppSpec


def test_define_derive_and_make_have_distinct_outputs():
    spec = defineAppSpec(title="Factory contract")
    app_type = deriveApp(title="Factory contract")
    column = makeColumn()
    operation = makeOp(alias="read", target="custom")
    assert issubclass(spec, AppSpec)
    assert app_type is not spec
    assert column.__class__.__name__ == "Column"
    assert operation.__class__.__name__ == "Op"


def test_make_factory_names_are_product_qualified():
    from importlib import import_module

    op_module = import_module("tigrbl_concrete.factories.op")
    assert not hasattr(op_module, "make")
    assert op_module.op is op_module.makeOp
