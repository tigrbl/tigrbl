from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from .serde import SerdeMixin


@dataclass(frozen=True)
class WebhookSpec(SerdeMixin):
    """Authoring input for an inbound HTTP POST operation."""

    path: str
    provider: str
    event_type: str
    handler: Callable[..., Any] | None = None
    alias: str | None = None
    proto: Literal["http.rest", "https.rest"] = "https.rest"
    request_model: Any | None = None
    response_model: Any | None = None
    status_code: int = 202
    security_deps: Sequence[Any] = ()
    extra: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.path.startswith("/") or "?" in self.path or "#" in self.path:
            raise ValueError("WebhookSpec.path must be an absolute HTTP path")
        if not self.provider or not self.event_type:
            raise ValueError("WebhookSpec requires provider and event_type")
        if self.proto not in {"http.rest", "https.rest"}:
            raise ValueError("WebhookSpec requires an HTTP REST binding")
        if not 200 <= self.status_code < 300:
            raise ValueError("Webhook acknowledgement must have a 2xx status")
        object.__setattr__(self, "security_deps", tuple(self.security_deps))
