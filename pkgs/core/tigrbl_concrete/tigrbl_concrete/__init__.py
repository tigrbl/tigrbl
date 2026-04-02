"""tigrbl_concrete compatibility facade with lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_COMPAT_ALIASES = {
    'ddl': 'tigrbl.ddl',
    'system': 'tigrbl.system',
    'op': 'tigrbl.op',
    'config': 'tigrbl.config',
    'schema': 'tigrbl.schema',
    'security': 'tigrbl.security',
}

__all__ = [
    'build_handlers',
    'build_hooks',
    'build_schemas',
    'build_rest_router',
    *_COMPAT_ALIASES,
]


def __getattr__(name: str) -> Any:
    if name in _COMPAT_ALIASES:
        module = import_module(_COMPAT_ALIASES[name])
        globals()[name] = module
        return module
    if name == 'build_handlers':
        fn = import_module('tigrbl_concrete._mapping.model')._materialize_handlers
    elif name == 'build_hooks':
        fn = import_module('tigrbl_concrete._mapping.model')._bind_model_hooks
    elif name == 'build_schemas':
        fn = import_module('tigrbl_concrete._mapping.model')._materialize_schemas
    elif name == 'build_rest_router':
        def fn(*args, **kwargs):
            if 'router' not in kwargs:
                kwargs['router'] = None
            return import_module('tigrbl_concrete._mapping.model')._materialize_rest_router(*args, **kwargs)
    else:
        raise AttributeError(name)
    globals()[name] = fn
    return fn
