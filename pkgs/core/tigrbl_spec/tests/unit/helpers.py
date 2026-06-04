from __future__ import annotations

from tigrbl_spec import with_identity


def app_payload() -> dict[str, object]:
    return with_identity(
        "AppSpec",
        {
            "title": "Tigrbl",
            "description": None,
            "version": "0.1.0",
            "execution_backend": "auto",
            "engine": None,
            "routers": {"__tuple__": []},
            "ops": {"__tuple__": []},
            "tables": {"__tuple__": []},
            "schemas": {"__tuple__": []},
            "hooks": {"__tuple__": []},
            "security_deps": {"__tuple__": []},
            "deps": {"__tuple__": []},
            "response": None,
            "jsonrpc_prefix": "/rpc",
            "system_prefix": "/system",
            "middlewares": {"__tuple__": []},
            "lifespan": None,
        },
    )
