from __future__ import annotations

import tigrbl

from tigrbl import TigrblApp, TigrblRouter
from tigrbl.factories.column import acol, makeColumn, makeVirtualColumn, vcol
from tigrbl.shortcuts.rest import get as shortcut_get
from tigrbl_kernel import Kernel


def _route_specs(owner):
    route_model = owner.tables["__tigrbl_route_ops__"]
    return tuple(getattr(getattr(route_model, "ops", None), "all", ()) or ())


def test_app_add_route_materializes_neutral_route_op_carrier() -> None:
    app = TigrblApp(title="HTTP Route Registration")

    def health() -> dict[str, bool]:
        return {"ok": True}

    app.add_route("/healthz", health, methods=["GET", "POST"], name="health")

    spec = next(item for item in _route_specs(app) if getattr(item, "alias", None) == "health")
    binding = spec.bindings[0]

    assert spec.target == "custom"
    assert binding.path == "/healthz"
    assert binding.methods == ("GET", "POST")


def test_duplicate_route_alias_merges_http_bindings() -> None:
    app = TigrblApp(title="HTTP Route Re-registration")

    def health() -> dict[str, bool]:
        return {"ok": True}

    app.add_route("/healthz", health, methods=["GET"], name="health")
    app.add_route("/system/healthz", health, methods=["GET"], name="health")
    app.add_route("/healthz", health, methods=["POST"], name="health")

    specs = [item for item in _route_specs(app) if getattr(item, "alias", None) == "health"]
    assert len(specs) == 1

    bindings = tuple(specs[0].bindings)
    assert len(bindings) == 2
    primary = next(binding for binding in bindings if binding.path == "/healthz")
    secondary = next(binding for binding in bindings if binding.path == "/system/healthz")
    assert primary.methods == ("GET", "POST")
    assert secondary.methods == ("GET",)


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


def test_system_document_mounts_register_as_ordinary_route_backed_ops() -> None:
    app = TigrblApp(title="System Route Registration")

    aliases = {getattr(item, "alias", None) for item in _route_specs(app)}
    doc_routes = {route.name: route for route in app.routes}

    assert "__openapi__" in aliases
    assert "__docs__" in aliases
    assert "openrpc_json" in aliases
    assert "__lens__" in aliases
    assert "__json_schema__" in aliases
    assert "__asyncapi__" in aliases
    assert doc_routes["__openapi__"].inherit_owner_dependencies is False
    assert doc_routes["__docs__"].inherit_owner_dependencies is False


def test_kernel_plan_indexes_registered_http_route_bindings_without_kernel_changes() -> None:
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


def test_public_surface_no_longer_exports_legacy_http_registration_helper() -> None:
    legacy_name = "register_" "http_route"

    assert legacy_name not in getattr(tigrbl, "__all__", ())
    assert not hasattr(tigrbl, legacy_name)


def test_shortcuts_reexport_factory_aliases_and_rest_decorators() -> None:
    assert acol is makeColumn
    assert vcol is makeVirtualColumn
    assert shortcut_get is tigrbl.get
