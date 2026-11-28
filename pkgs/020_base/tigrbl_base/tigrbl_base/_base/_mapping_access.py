from __future__ import annotations

from typing import Any


class AttrDict(dict):
    """Dictionary that also supports attribute-style access."""

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - trivial
        try:
            return self[item]
        except KeyError as e:  # pragma: no cover - debug helper
            raise AttributeError(item) from e

    def __setattr__(self, key: str, value: Any) -> None:  # pragma: no cover - trivial
        self[key] = value

    def __delattr__(self, item: str) -> None:
        try:
            del self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


__all__ = ["AttrDict"]
