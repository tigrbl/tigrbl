from types import SimpleNamespace

from tigrbl_atoms.route_handler import RouteHandlerDeclaration
from tigrbl_concrete._concrete._route import ROUTE_OPS_MODEL_NAME, add_route
from tigrbl_concrete._concrete.dependencies import Depends


def test_route_registration_leaves_dependency_invocation_to_the_plan():
    async def database_session():
        raise AssertionError("registration executed the dependency")
        yield

    async def handler(db=Depends(database_session)):
        return {"db": db}

    owner = SimpleNamespace(routes=[], tables={}, tags=None, prefix="")
    add_route(owner, "/probe", handler, methods=("GET",), name="probe")
    declaration, = owner.tables[ROUTE_OPS_MODEL_NAME].hooks.probe.HANDLER
    assert isinstance(declaration, RouteHandlerDeclaration)
    assert declaration.handler is handler
