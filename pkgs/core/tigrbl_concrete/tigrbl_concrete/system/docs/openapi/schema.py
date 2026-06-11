"""OpenAPI document builder for std routers."""

from __future__ import annotations

from typing import Any

JSON_SCHEMA_DRAFT_2020_12_DIALECT = "https://json-schema.org/draft/2020-12/schema"

from tigrbl_typing.status.mappings import status
from .helpers import (
    _request_schema_from_handler,
    _resolve_component_schema_ref,
    _schema_from_model,
    _security_from_dependencies,
    _security_schemes_from_dependencies,
)
from tigrbl_concrete._mapping.appspec.docs_lowering import (
    selected_projection_entries_if_configured,
)
from ..surface import auth_surface, binding_surface, op_surface


def _prefixed_path(router: Any, path: str) -> str:
    prefix = str(getattr(router, "_tigrbl_route_prefix", "") or "").rstrip("/")
    if not prefix:
        return path
    canonical = path if path.startswith("/") else f"/{path}"
    return f"{prefix}{canonical}" or "/"


def _selected_openapi_keys(
    router: Any,
    *,
    docs_path: str | None,
) -> set[tuple[str, str, str]] | None:
    selected = selected_projection_entries_if_configured(
        router,
        docs_path=docs_path,
        payload_kind="openapi",
    )
    if selected is None:
        return None
    if not selected:
        return set()
    return {
        (entry.path, str(entry.table or ""), str(entry.op or ""))
        for entry in selected
    }


def openapi(
    router: Any,
    *,
    docs_path: str | None = None,
    request: Any | None = None,
) -> dict[str, Any]:
    paths: dict[str, Any] = {}
    components: dict[str, Any] = {"schemas": {}}
    components_schemas: dict[str, Any] = components["schemas"]
    selected_keys = _selected_openapi_keys(router, docs_path=docs_path)
    del request

    for route in getattr(router, "_routes", []):
        if not route.include_in_schema:
            continue

        canonical_path = route.path_template.rstrip("/") or "/"
        if canonical_path == "/openrpc.json" or route.name == "openrpc_json":
            continue
        model = getattr(route, "tigrbl_model", None)
        route_alias = (
            getattr(route, "tigrbl_alias", None)
            or route.name.rsplit(".", maxsplit=1)[-1]
        )
        if selected_keys is not None:
            table_name = getattr(model, "__name__", "") if model is not None else ""
            if (canonical_path, table_name, str(route_alias)) not in selected_keys:
                continue

        output_path = _prefixed_path(router, canonical_path)
        path_item = paths.setdefault(output_path, {})
        for method in sorted(route.methods):
            alias = (
                getattr(route, "tigrbl_alias", None)
                or route.name.rsplit(".", maxsplit=1)[-1]
            )
            status_code = route.status_code or (
                status.HTTP_201_CREATED if alias == "create" else status.HTTP_200_OK
            )
            responses: dict[str, Any] = {}
            if route.responses:
                for code, meta in route.responses.items():
                    entry: dict[str, Any] = {
                        "description": meta.get("description", "") or "",
                    }
                    model = meta.get("model")
                    if model is not None:
                        entry["content"] = {
                            "application/json": {
                                "schema": _schema_from_model(
                                    model,
                                    components_schemas,
                                )
                            }
                        }
                    responses[str(code)] = entry
            if str(status_code) not in responses:
                entry = {"description": "Successful Response"}
                schema = route.response_schema
                if schema is None and route.response_model is not None:
                    schema = _schema_from_model(
                        route.response_model,
                        components_schemas,
                    )
                if schema is not None:
                    entry["content"] = {"application/json": {"schema": schema}}
                responses[str(status_code)] = entry

            op: dict[str, Any] = {
                "operationId": route.operation_id or route.name,
                "responses": responses,
            }
            if route.summary:
                op["summary"] = route.summary
            if route.description:
                op["description"] = route.description
            if route.tags:
                op["tags"] = route.tags
            if route.deprecated:
                op["deprecated"] = True

            params: list[dict[str, Any]] = []
            for param_name in route.param_names:
                schema = (route.path_param_schemas or {}).get(param_name) or {
                    "type": "string"
                }
                params.append(
                    {
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "schema": schema,
                    }
                )

            for qname, qschema in (route.query_param_schemas or {}).items():
                params.append(
                    {
                        "name": qname,
                        "in": "query",
                        "required": bool(qschema.get("required", False)),
                        "schema": {k: v for k, v in qschema.items() if k != "required"},
                    }
                )

            if params:
                op["parameters"] = params

            request_schema = route.request_schema
            if request_schema is None and route.request_model is not None:
                request_schema = _schema_from_model(
                    route.request_model,
                    components_schemas,
                )

            if request_schema is None:
                request_schema = _request_schema_from_handler(route, components_schemas)

            if isinstance(request_schema, dict) and alias.startswith("bulk_"):
                request_schema = _resolve_component_schema_ref(
                    request_schema,
                    components_schemas,
                )

            if request_schema is not None:
                op["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": request_schema}},
                }

            model = getattr(route, "tigrbl_model", None)
            alias = getattr(route, "tigrbl_alias", None)
            binding = getattr(route, "tigrbl_binding", None)
            security_deps: list[Any] = []
            security_deps.extend(list(getattr(router, "dependencies", None) or ()))
            security_deps.extend(list(getattr(route, "dependencies", None) or ()))
            security_deps.extend(
                list(getattr(route, "security_dependencies", None) or ())
            )
            surface_spec = None
            if model is not None and isinstance(alias, str):
                specs = getattr(getattr(model, "ops", None), "by_alias", {})
                sp_list = specs.get(alias) or ()
                if sp_list:
                    surface_spec = sp_list[0]
                    security_deps.extend(
                        list(getattr(sp_list[0], "security_deps", ()) or ())
                    )

            for dep in tuple(getattr(route, "dependencies", ()) or ()):
                if dep not in security_deps:
                    security_deps.append(dep)

            sec = _security_from_dependencies(security_deps)
            if sec:
                op["security"] = sec
                components.setdefault("securitySchemes", {}).update(
                    _security_schemes_from_dependencies(security_deps)
                )
            op["x-tigrbl-auth"] = auth_surface(sec)

            surface = (
                op_surface(surface_spec)
                if surface_spec is not None
                else {}
            )
            exchange = getattr(route, "tigrbl_exchange", None)
            if exchange not in (None, "request_response"):
                surface["exchange"] = exchange
            tx_scope = getattr(route, "tigrbl_tx_scope", None)
            if tx_scope not in (None, "inherit"):
                surface["txScope"] = tx_scope
            surface["binding"] = (
                binding_surface(binding) if binding is not None else None
            )
            op["x-tigrbl-surface"] = surface

            path_item[method.lower()] = op

    seen_paths = getattr(router, "_seen_paths", None)
    if isinstance(seen_paths, set):
        for raw_path in seen_paths:
            if not isinstance(raw_path, str):
                continue
            normalized = raw_path.rstrip("/") or "/"
            if normalized in paths:
                continue
            for templated, item in list(paths.items()):
                matcher = _template_matcher(templated)
                if matcher is None or matcher.match(normalized) is None:
                    continue
                paths[normalized] = item
                break

    doc: dict[str, Any] = {
        "openapi": "3.1.0",
        "jsonSchemaDialect": JSON_SCHEMA_DRAFT_2020_12_DIALECT,
        "info": {"title": router.title, "version": router.version},
        "paths": paths,
        "components": components,
    }
    if router.description:
        doc["info"]["description"] = router.description
    return doc


def _template_matcher(path_template: str):
    import re

    escaped = re.escape(path_template)
    pattern = re.sub(r"\\\{[A-Za-z_][A-Za-z0-9_]*\\\}", r"[^/]+", escaped)
    return re.compile(rf"^{pattern}$")
