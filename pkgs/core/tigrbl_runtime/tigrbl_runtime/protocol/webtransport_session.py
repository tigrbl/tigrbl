from __future__ import annotations

from typing import Any

from tigrbl_atoms.runtime_channel import WebTransportLaneState
from tigrbl_atoms.runtime_channel import (
    WebTransportSessionState as _AtomWebTransportSessionState,
)
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload


class WebTransportSessionState(_AtomWebTransportSessionState):
    def project_event(
        self,
        *,
        event: str,
        channel: str,
        payload: dict[str, Any],
    ) -> dict[str, object]:
        return validate_webtransport_event_payload(
            event=event,
            channel=channel,
            payload=payload,
        )


__all__ = ["WebTransportLaneState", "WebTransportSessionState"]
