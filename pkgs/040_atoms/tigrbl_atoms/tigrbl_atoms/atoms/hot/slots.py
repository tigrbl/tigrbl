from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class HotSlotPayload:
    field_names: tuple[str, ...]
    field_index: Mapping[str, int] | None
    values: Sequence[Any]
    present: bytes | bytearray | memoryview
    source_ref: Any = None

    def row_tuple(self, columns: Sequence[str] | None = None) -> tuple[Any, ...]:
        return project_row_tuple(
            self.field_names,
            self.field_index,
            self.values,
            self.present,
            columns=columns,
        )

    def as_mapping(self) -> "SlotMappingView":
        return SlotMappingView(
            self.field_names,
            self.field_index,
            self.values,
            self.present,
        )


class SlotMappingView(Mapping[str, Any]):
    __slots__ = ("_field_names", "_field_index", "_values", "_present")

    def __init__(
        self,
        field_names: tuple[str, ...],
        field_index: Mapping[str, int] | None,
        values: Sequence[Any],
        present: bytes | bytearray | memoryview,
    ) -> None:
        self._field_names = field_names
        self._field_index = field_index
        self._values = values
        self._present = present

    def __getitem__(self, key: str) -> Any:
        idx = _slot_index(self._field_names, self._field_index, key)
        if idx < 0 or idx >= len(self._values) or not _present(self._present, idx):
            raise KeyError(key)
        return self._values[idx]

    def __iter__(self) -> Iterator[str]:
        limit = min(len(self._field_names), len(self._values), len(self._present))
        for idx in range(limit):
            if _present(self._present, idx):
                yield self._field_names[idx]

    def __len__(self) -> int:
        limit = min(len(self._field_names), len(self._values), len(self._present))
        total = 0
        for idx in range(limit):
            if _present(self._present, idx):
                total += 1
        return total

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


def capture_slot_payload(ctx: Any) -> HotSlotPayload | None:
    hot = None
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, Mapping):
        candidate = temp.get("hot_ctx")
        if candidate is not None:
            hot = candidate
    if hot is None:
        hot = getattr(ctx, "hot_ctx", None)
    if hot is None:
        return None

    field_names = tuple(getattr(hot, "slot_field_names", ()) or ())
    values = getattr(hot, "assembled_slot_values", None)
    present = getattr(hot, "assembled_slot_present", None)
    if values is None or present is None:
        values = getattr(hot, "slot_values", None)
        present = getattr(hot, "slot_present", None)
    if not field_names or values is None or present is None:
        return None

    field_index = getattr(hot, "slot_field_index", None)
    if not isinstance(field_index, Mapping):
        field_index = None
    return HotSlotPayload(
        field_names=field_names,
        field_index=field_index,
        values=values,
        present=present,
        source_ref=getattr(hot, "body_view", None)
        or getattr(hot, "body_bytes", None)
        or getattr(hot, "parsed_json", None),
    )


def project_row_tuple(
    field_names: tuple[str, ...],
    field_index: Mapping[str, int] | None,
    values: Sequence[Any],
    present: bytes | bytearray | memoryview,
    *,
    columns: Sequence[str] | None = None,
) -> tuple[Any, ...]:
    names = columns if columns is not None else field_names
    row: list[Any] = []
    for name in names:
        idx = _slot_index(field_names, field_index, name)
        row.append(values[idx] if 0 <= idx < len(values) and _present(present, idx) else None)
    return tuple(row)


def project_present_dict(payload: HotSlotPayload) -> dict[str, Any]:
    return dict(payload.as_mapping())


def _slot_index(
    field_names: tuple[str, ...], field_index: Mapping[str, int] | None, name: str
) -> int:
    if field_index is not None:
        try:
            return int(field_index.get(name, -1))
        except Exception:
            return -1
    try:
        return field_names.index(name)
    except ValueError:
        return -1


def _present(present: bytes | bytearray | memoryview, idx: int) -> bool:
    try:
        return bool(present[idx])
    except Exception:
        return False


__all__ = [
    "HotSlotPayload",
    "SlotMappingView",
    "capture_slot_payload",
    "project_present_dict",
    "project_row_tuple",
]
