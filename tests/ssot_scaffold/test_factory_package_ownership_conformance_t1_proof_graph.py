from importlib import import_module


facade_column = import_module("tigrbl.factories.column")
facade_op = import_module("tigrbl.factories.op")
facade_router = import_module("tigrbl.factories.router")
column = import_module("tigrbl_concrete.factories.column")
op = import_module("tigrbl_concrete.factories.op")
router = import_module("tigrbl_concrete.factories.router")


def test_facade_reexports_concrete_factory_identity():
    assert facade_column.makeColumn is column.makeColumn
    assert facade_column.makeVirtualColumn is column.makeVirtualColumn
    assert facade_router.defineRouterSpec is router.defineRouterSpec
    assert facade_router.deriveRouter is router.deriveRouter
    assert facade_op.makeOp is op.makeOp
    assert facade_op.op is op.op
