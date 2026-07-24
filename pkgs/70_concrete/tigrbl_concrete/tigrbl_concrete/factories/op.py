from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._op import Op


def makeOp(**kwargs: Any) -> Op:
    """Make a concrete declarative operation descriptor."""
    return Op(**kwargs)


op = makeOp

__all__ = ["makeOp", "op"]
