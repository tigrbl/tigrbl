from __future__ import annotations

from typing import Any

from tigrbl_concrete.factories.webhook import DefineWebhook


def defineWebhook(**kwargs: Any):
    """Shortcut for defining an inbound webhook endpoint."""
    return DefineWebhook(**kwargs)


__all__ = ["defineWebhook"]
