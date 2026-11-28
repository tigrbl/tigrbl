from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tigrbl_kernel.opchannel_capabilities import capability_mask


class OpChannelCapabilityError(ValueError):
    def __init__(self, message: str, *, metadata: dict[str, object]) -> None:
        super().__init__(message)
        self.metadata = metadata


def verify_opchannel_capabilities(
    *,
    required: tuple[str, ...],
    adapter: Mapping[str, Any],
    binding: str | None = None,
    subevent: str | None = None,
) -> dict[str, object]:
    adapter_caps = tuple(str(item) for item in adapter.get("capabilities", ()) or ())
    required_caps = tuple(str(item) for item in required)
    required_mask = capability_mask(required_caps)
    adapter_mask = capability_mask(adapter_caps)
    missing = tuple(cap for cap in required_caps if cap not in adapter_caps)

    if adapter.get("stale") or missing:
        metadata: dict[str, object] = {
            "binding": binding,
            "subevent": subevent,
            "required": required_caps,
            "adapter": adapter_caps,
            "missing": missing,
            "required_mask": required_mask,
            "adapter_mask": adapter_mask,
        }
        reason = "stale adapter" if adapter.get("stale") else f"missing {', '.join(missing)}"
        raise OpChannelCapabilityError(
            f"adapter capability handshake failed before execution: {reason}",
            metadata=metadata,
        )

    return {
        "passed": True,
        "required": required_caps,
        "adapter": adapter_caps,
        "missing": (),
        "required_mask": required_mask,
        "adapter_mask": adapter_mask,
        "capability_mask": adapter_mask,
    }


__all__ = ["OpChannelCapabilityError", "verify_opchannel_capabilities"]
