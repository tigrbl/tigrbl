from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ERR_TRANSPORT_SHAPE


async def run(obj: object | None, ctx: Any) -> None:
    from ..response.error_to_transport import _run as _shape_error_response

    await _shape_error_response(obj, ctx)


__all__ = ["ANCHOR", "run"]
