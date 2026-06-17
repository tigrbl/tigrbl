from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Webhook:
    """Concrete inbound webhook endpoint authoring object.

    This object describes inbound webhook ingress. It is not a core spec and
    does not execute authentication, idempotency, acknowledgement, or request
    handling behavior. Factories lower it into canonical PathSpec and OpSpec
    objects for the kernel/compiler pipeline.
    """

    path: str
    provider: str
    event_type: str
    handler: Callable[..., Any] | None = None
    alias: str | None = None
    proto: str = "https.rest"
    request_model: Any | None = None
    response_model: Any | None = None
    status_code: int = 202
    security_deps: Sequence[Any] = ()
    extra: dict[str, Any] | None = None


__all__ = ["Webhook"]
