from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def compile_callback_metadata(callbacks: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    compiled: list[dict[str, object]] = []
    for callback in callbacks:
        name = str(callback["name"])
        language = str(callback.get("language") or "python")
        row = {
            "name": name,
            "kind": callback.get("kind"),
            "language": language,
            "phase": callback.get("phase"),
            "callback_ref": name,
            "ffi_boundary": language,
        }
        compiled.append({key: value for key, value in row.items() if value is not None})
    return compiled


__all__ = ["compile_callback_metadata"]
