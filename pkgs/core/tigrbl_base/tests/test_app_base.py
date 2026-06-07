from tigrbl_base._base._app_base import AppBase
from tigrbl_core._spec.app_spec import AppSpec


def test_app_base_defaults() -> None:
    app = AppBase()

    assert isinstance(app, AppSpec)
    assert app.title == "Tigrbl"
    assert app.version == "0.1.0"
    assert app.jsonrpc_prefix == "/rpc"
    assert app.system_prefix == "/system"


def test_collect_spec_normalizes_and_collects() -> None:
    class Parent:
        TITLE = "Parent"
        VERSION = "1.0.0"
        EXECUTION_BACKEND = "rust"
        ROUTERS = ("r1",)

    class Child(Parent):
        DESCRIPTION = "desc"
        OPS = ("op1",)
        TABLES = ("table1",)
        SCHEMAS = ("schema1",)
        HOOKS = ("hook1",)
        SECURITY_DEPS = ("sec",)
        DEPS = ("dep",)
        MIDDLEWARES = ("mw",)

    spec = AppBase.collect_spec(Child)

    assert isinstance(spec, AppSpec)
    assert spec.title == "Parent"
    assert spec.description == "desc"
    assert spec.version == "1.0.0"
    assert spec.execution_backend == "rust"
    assert spec.routers == ("r1",)
    assert spec.ops == ("op1",)
    assert spec.tables == ("table1",)
    assert spec.schemas == ("schema1",)
    assert spec.hooks == ("hook1",)
    assert spec.security_deps == ("sec",)
    assert spec.deps == ("dep",)
    assert spec.middlewares == ("mw",)


def test_collect_spec_deduplicates_routers_without_dropping_child_order() -> None:
    class Parent:
        ROUTERS = ("root",)

    class Child(Parent):
        ROUTERS = ("api", "api", "admin")

    spec = AppBase.collect_spec(Child)

    assert spec.routers == ("api", "admin", "root")


def test_bind_spec_normalizes_falsy_strings_and_sequences() -> None:
    spec = AppSpec(
        title="",
        version="",
        execution_backend="",
        jsonrpc_prefix="",
        system_prefix="",
        routers=["api"],
        ops=None,
        tables=None,
        schemas=None,
        hooks=None,
        security_deps=None,
        deps=None,
        middlewares=None,
    )

    bound = AppBase.bind_spec(spec)

    assert bound.title == "Tigrbl"
    assert bound.version == "0.1.0"
    assert bound.execution_backend == "auto"
    assert bound.jsonrpc_prefix == "/rpc"
    assert bound.system_prefix == "/system"
    assert bound.routers == ("api",)
    assert bound.ops == ()
    assert bound.tables == ()
    assert bound.schemas == ()
    assert bound.hooks == ()
    assert bound.security_deps == ()
    assert bound.deps == ()
    assert bound.middlewares == ()
