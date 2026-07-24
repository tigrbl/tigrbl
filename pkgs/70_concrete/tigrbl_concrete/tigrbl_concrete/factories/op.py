from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._op import Op


def make(**kwargs: Any) -> Op:
    """Make a concrete declarative operation descriptor."""
    return Op(**kwargs)


op = make

__all__ = ["make", "op"]
