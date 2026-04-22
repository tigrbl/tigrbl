from tigrbl import (
    Binding,
    BindingRegistry,
    BindingRegistrySpec,
    BindingSpec,
    build_handlers,
    build_rest,
    get,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    Hook,
    OpSpec,
    SseBindingSpec,
    WsBindingSpec,
    hook_ctx,
    op_ctx,
    sse_ctx,
    stream_ctx,
    websocket_ctx,
    webtransport_ctx,
)
from tigrbl_core.config.constants import HOOK_DECLS_ATTR
from tests.conftest import mro_collect_decorated_ops


def test_opspec_accepts_exchange_tx_scope_and_security_deps_alias() -> None:
    spec = OpSpec(
        alias="stream",
        target="custom",
        exchange="server_stream",
        tx_scope="read_only",
        security_deps=("auth",),
    )

    assert spec.exchange == "server_stream"
    assert spec.tx_scope == "read_only"
    assert spec.security_deps == ("auth",)
    assert spec.secdeps == ("auth",)


def test_op_ctx_records_direct_binding_and_surface_attributes() -> None:
    class Widget:
        @op_ctx(
            alias="feed",
            target="custom",
            bindings=(HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/feed"),),
            exchange="server_stream",
            tx_scope="read_only",
            security_deps=("auth",),
            subevents=("chunk",),
        )
        def feed(cls, ctx):
            return None

    spec = mro_collect_decorated_ops(Widget)[0]
    assert spec.bindings[0].path == "/feed"
    assert spec.exchange == "server_stream"
    assert spec.tx_scope == "read_only"
    assert spec.security_deps == ("auth",)
    assert spec.subevents == ("chunk",)


def test_alias_surface_decorators_attach_expected_bindings() -> None:
    class Widget:
        @websocket_ctx("/ws", alias="socket", framing="jsonrpc")
        def socket(cls, ctx):
            return None

        @sse_ctx("/events", alias="events")
        def events(cls, ctx):
            return None

        @stream_ctx("/stream", alias="stream")
        def stream(cls, ctx):
            return None

        @webtransport_ctx("/transport", alias="transport")
        def transport(cls, ctx):
            return None

    specs = {spec.alias: spec for spec in mro_collect_decorated_ops(Widget)}
    assert isinstance(specs["socket"].bindings[0], WsBindingSpec)
    assert specs["socket"].bindings[0].framing == "jsonrpc"
    assert isinstance(specs["events"].bindings[0], SseBindingSpec)
    assert specs["events"].exchange == "server_stream"
    assert specs["stream"].bindings[0].framing == "stream"
    assert specs["transport"].bindings[0].proto == "webtransport"


def test_get_decorator_attaches_explicit_http_rest_binding() -> None:
    class Widget:
        @get("/feed", alias="feed")
        def feed(cls, ctx):
            return None

    specs = tuple(mro_collect_decorated_ops(Widget))
    build_handlers(Widget, specs)
    build_rest(Widget, specs)

    spec = next(item for item in tuple(getattr(getattr(Widget, "ops", None), "all", ()) or ()) if item.alias == "feed")
    binding = spec.bindings[0]

    assert isinstance(binding, HttpRestBindingSpec)
    assert binding.path.endswith("/feed")
    assert binding.methods == ("GET",)
    assert spec.target == "custom"


def test_hook_ctx_records_direct_selector_declaration() -> None:
    class Widget:
        @hook_ctx(
            ops="feed",
            phase="PRE_HANDLER",
            bindings=("http.stream",),
            exchange="server_stream",
            family=("custom",),
            subevents=("chunk",),
        )
        def observe(cls, ctx):
            return None

    decls = getattr(Widget.observe.__func__, HOOK_DECLS_ATTR)
    assert isinstance(decls[0], Hook)
    assert decls[0].bindings == ("http.stream",)
    assert decls[0].exchange == "server_stream"
    assert decls[0].family == ("custom",)
    assert decls[0].subevents == ("chunk",)


def test_public_facade_exports_binding_surface_types() -> None:
    binding = BindingSpec(
        name="rpc",
        spec=HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.rpc"),
    )
    registry = BindingRegistrySpec()
    registry.register(binding)

    assert Binding is not None
    assert BindingRegistry is not None
    assert registry.get("rpc") == binding
