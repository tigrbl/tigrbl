from __future__ import annotations

from collections.abc import Callable
import re
from typing import Any

from tigrbl_core._spec import HttpRestBindingSpec, OpSpec, PathSpec
from tigrbl_concrete._concrete._webhook import Webhook


def DefineWebhook(
    *,
    path: str,
    provider: str,
    event_type: str,
    handler: Callable[..., Any] | None = None,
    alias: str | None = None,
    proto: str = "https.rest",
    request_model: Any | None = None,
    response_model: Any | None = None,
    status_code: int = 202,
    security_deps: tuple[Any, ...] = (),
    extra: dict[str, Any] | None = None,
) -> PathSpec:
    """Define an inbound webhook endpoint and lower it to a core PathSpec."""
    webhook = Webhook(
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
    return _buildWebhookPathSpec(webhook)


def _buildWebhookPathSpec(webhook: Webhook) -> PathSpec:
    selected_alias = webhook.alias or _webhookAlias(
        provider=webhook.provider,
        event_type=webhook.event_type,
    )
    binding = HttpRestBindingSpec(
        proto=webhook.proto,  # type: ignore[arg-type]
        methods=("POST",),
        path=webhook.path,
    )
    metadata = {
        "direction": "inbound",
        "provider": webhook.provider,
        "event_type": webhook.event_type,
        **dict(webhook.extra or {}),
    }
    op = OpSpec(
        alias=selected_alias,
        target="custom",
        expose_rpc=False,
        bindings=(binding,),
        http_methods=("POST",),
        status_code=webhook.status_code,
        request_model=webhook.request_model,
        response_model=webhook.response_model,
        handler=webhook.handler,
        security_deps=tuple(webhook.security_deps or ()),
        extra={"webhook": metadata},
    )
    return PathSpec(path=webhook.path, kind="resource", name=selected_alias, ops=(op,))


def _webhookAlias(*, provider: str, event_type: str) -> str:
    token = f"{provider}_{event_type}".lower()
    token = re.sub(r"[^a-z0-9_]+", "_", token).strip("_")
    token = re.sub(r"_+", "_", token)
    return f"webhook_{token or 'event'}"


__all__ = ["DefineWebhook"]
