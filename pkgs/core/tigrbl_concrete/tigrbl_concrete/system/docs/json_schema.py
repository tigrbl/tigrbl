from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.http_routes import register_http_route
from tigrbl_concrete.system.docs.openapi.schema import JSON_SCHEMA_DRAFT_2020_12_DIALECT, openapi


def _build_json_schema_bundle(router: Any) -> dict[str, Any]:
    spec = openapi(router)
    return {
        '$schema': JSON_SCHEMA_DRAFT_2020_12_DIALECT,
        '$defs': dict(spec.get('components', {}).get('schemas', {}) or {}),
    }


def _mount_json_schema(router: Any, *, path: str = '/schemas.json', name: str = '__json_schema__') -> Any:
    normalized_path = path if str(path).startswith('/') else f'/{path}'

    def _json_schema_handler(_request: Any) -> Response:
        return Response.json(_build_json_schema_bundle(router))

    register_http_route(router, path=normalized_path, methods=("GET",), alias=name, endpoint=_json_schema_handler)
    router.add_route(normalized_path, _json_schema_handler, methods=['GET'], name=name, include_in_schema=False)
    return router


__all__ = ['_build_json_schema_bundle', '_mount_json_schema']
