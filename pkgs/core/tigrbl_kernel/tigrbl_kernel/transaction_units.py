from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

_ALLOWED = {"handler", "none"}


def compile_subevent_tx_units(rows: Iterable[Mapping[str, Any]]) -> dict[tuple[str, str, str], str]:
    units: dict[tuple[str, str, str], str] = {}
    for row in rows:
        tx_unit = str(row.get("tx_unit", "none"))
        family = str(row.get("family", ""))
        subevent = str(row.get("subevent", ""))
        phase = str(row.get("phase", ""))
        if tx_unit not in _ALLOWED:
            raise ValueError("transaction tx_unit invalid for subevent")
        if tx_unit != "none" and subevent.endswith(".close"):
            raise ValueError("transport close subevent cannot open transaction tx_unit")
        units[(family, subevent, phase)] = tx_unit
    return units


__all__ = ["compile_subevent_tx_units"]
