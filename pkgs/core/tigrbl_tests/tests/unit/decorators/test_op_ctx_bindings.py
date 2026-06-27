from types import SimpleNamespace

from tigrbl import Router, TigrblApp, op_ctx
from tigrbl_core._spec.op_spec import OpSpec


def test_op_ctx_internal_binding_returns_classmethod_with_spec():
    @op_ctx(alias="search", target="custom", status_code=201)
    def search(cls, ctx):
        return ctx

    class Widget:
        lookup = search

    method = Widget.__dict__["lookup"]
    assert isinstance(method, classmethod)
    decl = method.__func__.__tigrbl_op_spec__
    assert decl.alias == "search"
    assert decl.target == "custom"
    assert decl.status_code == 201
    assert method.__func__.__tigrbl_ctx_only__ is True


def test_op_ctx_external_binding_to_multiple_table_classes():
    class Alpha:
        pass

    class Beta:
        pass

    @op_ctx(alias="touch", target="custom", bind=[Alpha, Beta])
    def touch(cls, ctx):
        return {"touched": True}

    for model in (Alpha, Beta):
        method = model.__dict__["touch"]
        assert isinstance(method, classmethod)
        decl = method.__func__.__tigrbl_op_spec__
        assert decl.alias == "touch"
        assert decl.target == "custom"


def test_op_ctx_external_binding_registers_op_on_target_class():
    class Widget:
        pass

    @op_ctx(
        alias="recompute",
        target="custom",
        arity="member",
        rest=False,
        bind=Widget,
    )
    async def recompute(cls, ctx):
        return {"payload": ctx.get("payload")}

    method = Widget.__dict__["recompute"]
    assert isinstance(method, classmethod)

    registered = Widget.__tigrbl_ops__[-1]
    assert registered.alias == "recompute"
    assert registered.target == "custom"
    assert registered.arity == "member"
    assert registered.expose_routes is False
    assert registered.handler is not None


def test_op_ctx_external_binding_can_be_called_from_table_class():
    class Widget:
        pass

    @op_ctx(alias="diagnostics", target="custom", bind=Widget)
    def diagnostics(cls, ctx):
        return {"model": cls.__name__, "payload": ctx["payload"]}

    assert Widget.diagnostics({"payload": "ready"}) == {
        "model": "Widget",
        "payload": "ready",
    }


def test_op_ctx_external_binding_merges_existing_op_declaration():
    class Widget:
        __tigrbl_ops__ = (
            OpSpec(
                alias="diagnostics",
                target="custom",
                arity="collection",
                http_methods=("GET",),
            ),
        )

    @op_ctx(
        alias="diagnostics",
        target="custom",
        arity="member",
        rest=False,
        bind=Widget,
    )
    def diagnostics(cls, ctx):
        return {"ok": True}

    assert len(Widget.__tigrbl_ops__) == 1
    registered = Widget.__tigrbl_ops__[0]
    assert registered.alias == "diagnostics"
    assert registered.target == "custom"
    assert registered.arity == "member"
    assert registered.expose_routes is False
    assert registered.http_methods == ("GET",)
    assert registered.handler is not None


def test_op_ctx_binding_to_app_instance_uses_classmethod_descriptor():
    class ExampleApp(TigrblApp):
        TITLE = "Example"
        VERSION = "0.1.0"
        LIFESPAN = None

    app = ExampleApp()

    @op_ctx(alias="diagnostics", target="custom", bind=app)
    def diagnostics(cls, ctx):
        return {"ok": True}

    bound = app.__dict__["diagnostics"]
    assert isinstance(bound, classmethod)
    assert bound.__func__.__tigrbl_op_spec__.alias == "diagnostics"


def test_op_ctx_binding_to_router_class():
    class ExampleRouter(Router):
        PREFIX = ""
        NAME = "example"

    @op_ctx(alias="hook", target="custom", bind=ExampleRouter)
    def hook(cls, ctx):
        return None

    method = ExampleRouter.__dict__["hook"]
    assert isinstance(method, classmethod)
    assert method.__func__.__tigrbl_op_spec__.alias == "hook"


def test_op_ctx_binding_to_plain_object():
    target = SimpleNamespace()

    @op_ctx(alias="noop", target="custom", bind=target)
    def noop(cls, ctx):
        return None

    bound = target.__dict__["noop"]
    assert isinstance(bound, classmethod)
    assert bound.__func__.__tigrbl_op_spec__.alias == "noop"
