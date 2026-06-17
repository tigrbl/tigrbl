from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from tigrbl_concrete.factories.webhook import DefineWebhook

_T = TypeVar("_T", bound=Callable[..., Any])


def webhook(
    *,
    path: str,
    provider: str,
    event_type: str,
    alias: str | None = None,
    proto: str = "https.rest",
    request_model: Any | None = None,
    response_model: Any | None = None,
    status_code: int = 202,
    security_deps: tuple[Any, ...] = (),
    extra: dict[str, Any] | None = None,
) -> Callable[[_T], _T]:
    """Decorate a handler with an inbound webhook endpoint PathSpec."""

    def _decorate(handler: _T) -> _T:
        path_spec = DefineWebhook(
            path=path,
            provider=provider,
            event_type=event_type,
            handler=handler,
            alias=alias,
            proto=proto,
            request_model=request_model,
            response_model=response_model,
            status_code=status_code,
            security_deps=tuple(security_deps or ()),
            extra=dict(extra or {}),
        )
        setattr(handler, "__tigrbl_webhook_path_spec__", path_spec)
        return handler

    return _decorate


__all__ = ["webhook"]
