from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_get_route

ASYNCAPI_VERSION = '2.6.0'


def _build_asyncapi_spec(router: Any) -> dict[str, Any]:
    channels: dict[str, Any] = {}
    for route in list(getattr(router, 'websocket_routes', []) or []):
        entry: dict[str, Any] = {'subscribe': {'operationId': route.name}}
        if route.summary:
            entry['subscribe']['summary'] = route.summary
        if route.description:
            entry['subscribe']['description'] = route.description
        channels[route.path_template] = entry
    return {
        'asyncapi': ASYNCAPI_VERSION,
        'info': {
            'title': getattr(router, 'title', 'API'),
            'version': getattr(router, 'version', '0.1.0'),
        },
        'channels': channels,
    }


def _mount_asyncapi(router: Any, *, path: str = '/asyncapi.json', name: str = '__asyncapi__') -> Any:
    normalized_path = path if str(path).startswith('/') else f'/{path}'

    def _asyncapi_handler(_request: Any) -> Response:
        return Response.json(_build_asyncapi_spec(router))

    register_runtime_get_route(router, path=normalized_path, alias=name, endpoint=_asyncapi_handler)
    router.add_route(normalized_path, _asyncapi_handler, methods=['GET'], name=name, include_in_schema=False)
    return router


__all__ = ['ASYNCAPI_VERSION', '_build_asyncapi_spec', '_mount_asyncapi']
