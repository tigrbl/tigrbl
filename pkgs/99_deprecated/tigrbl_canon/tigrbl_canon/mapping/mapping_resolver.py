from __future__ import annotations

from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)


from .precedence import key_for, merge_op_specs

__all__ = ["merge_op_specs", "key_for"]
