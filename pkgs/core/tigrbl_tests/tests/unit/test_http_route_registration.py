from __future__ import annotations

from tigrbl import TigrblApp, TigrblRouter, register_http_route
from tigrbl_kernel import Kernel


def _route_specs(owner):
    system_model = owner.tables["__tigrbl_system_routes__"]
    return tuple(getattr(getattr(system_model, "ops", None), "all", ()) or ())


def test_register_http_route_creates_concrete_custom_op() -> None:
    app = TigrblApp(title="HTTP Route Registration")

    def health() -> dict[str, bool]:
        return {"ok": True}

    register_http_route(
        app,
        path="/healthz",
        methods=("GET", "POST"),
        alias="health",
        endpoint=health,
    )

    spec = next(item for item in _route_specs(app) if getattr(item, "alias", None) == "health")
    binding = spec.bindings[0]

    assert spec.target == "custom"
    assert binding.path == "/healthz"
    assert binding.methods == ("GET", "POST")


def test_register_http_route_reregistration_updates_existing_alias() -> None:
    app = TigrblApp(title="HTTP Route Re-registration")

    def health() -> dict[str, bool]:
        return {"ok": True}

    register_http_route(app, path="/healthz", methods=("GET",), alias="health", endpoint=health)
    register_http_route(app, path="/system/healthz", methods=("GET",), alias="health", endpoint=health)
    register_http_route(app, path="/healthz", methods=("POST",), alias="health", endpoint=health)

    specs = [item for item in _route_specs(app) if getattr(item, "alias", None) == "health"]
    assert len(specs) == 1

    bindings = tuple(specs[0].bindings)
    assert len(bindings) == 2
    primary = next(binding for binding in bindings if binding.path == "/healthz")
    secondary = next(binding for binding in bindings if binding.path == "/system/healthz")
    assert primary.methods == ("GET", "POST")
    assert secondary.methods == ("GET",)


def test_app_add_route_registers_concrete_http_binding() -> None:
    app = TigrblApp(title="App Route Registration")

    def health() -> dict[str, bool]:
        return {"ok": True}

    app.add_route("/healthz", health, methods=["GET"], name="health")

    spec = next(item for item in _route_specs(app) if getattr(item, "alias", None) == "health")
    assert spec.bindings[0].path == "/healthz"
    assert spec.bindings[0].methods == ("GET",)


def test_router_routes_register_prefixed_bindings_on_app_include() -> None:
    app = TigrblApp(title="Prefixed Route Registration")
    router = TigrblRouter()

    def health() -> dict[str, bool]:
        return {"ok": True}

    router.add_route("/healthz", health, methods=["GET"], name="health")
    app.include_router(router, prefix="/system")

    spec = next(item for item in _route_specs(app) if getattr(item, "alias", None) == "health")
    assert spec.bindings[0].path == "/system/healthz"
    assert spec.bindings[0].methods == ("GET",)


def test_system_document_mounts_register_via_concrete_http_routes() -> None:
    app = TigrblApp(title="System Route Registration")

    aliases = {getattr(item, "alias", None) for item in _route_specs(app)}

    assert "__openapi__" in aliases
    assert "__docs__" in aliases
    assert "openrpc_json" in aliases
    assert "__lens__" in aliases


def test_kernel_plan_indexes_registered_http_route_bindings() -> None:
    app = TigrblApp(title="Kernel Route Registration")

    def health() -> dict[str, bool]:
        return {"ok": True}

    app.add_route("/healthz", health, methods=["GET"], name="health")

    plan = Kernel().compile_plan(app)
    rest_index = plan.proto_indices["http.rest"]
    exact = rest_index.get("exact", rest_index) if isinstance(rest_index, dict) else rest_index

    assert "GET /healthz" in exact
    meta = plan.opmeta[exact["GET /healthz"]]
    assert meta.alias == "health"
