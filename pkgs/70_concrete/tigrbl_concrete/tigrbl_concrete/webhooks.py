from __future__ import annotations

from tigrbl_concrete._concrete._webhook import (
    Webhook,
)
from tigrbl_concrete.factories.webhook import DefineWebhook
from tigrbl_concrete.shortcuts.webhook import defineWebhook

__all__ = [
    "DefineWebhook",
    "Webhook",
    "defineWebhook",
]
